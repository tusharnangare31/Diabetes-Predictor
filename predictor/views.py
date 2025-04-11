from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.core.cache import cache
from django.db.models import Avg, Max, Min
from django.conf import settings

import pickle
import numpy as np
import os
import json
import logging
from datetime import datetime, timedelta

from .forms import (
    CustomUserCreationForm, CustomAuthenticationForm, UserProfileForm,
    RiskAssessmentForm, LifestyleTrackingForm, ProgressTrackingForm,
    DiabetesPredictionForm
)
from .models import (
    UserProfile, RiskAssessment, LifestyleTracking, 
    ProgressTracking, DiabetesRiskPrediction
)

# Setup logger
logger = logging.getLogger(__name__)

# Cache timeouts
DASHBOARD_CACHE_TIMEOUT = 60 * 5  # 5 minutes
PREDICTION_MODEL_CACHE_TIMEOUT = 60 * 60 * 24  # 24 hours

def get_prediction_model():
    """Get cached prediction model or load it from file"""
    model = cache.get('prediction_model')
    if model is None:
        try:
            model_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'classification_model.pkl')
            with open(model_path, 'rb') as file:
                model = pickle.load(file)
            cache.set('prediction_model', model, PREDICTION_MODEL_CACHE_TIMEOUT)
        except Exception as e:
            logger.error(f"Error loading prediction model: {str(e)}")
            raise
    return model

def home(request):
    """Home page view"""
    return render(request, 'predictor/home.html')

@require_http_methods(["GET", "POST"])
def register(request):
    """User registration view with improved validation"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                login(request, user)
                messages.success(request, "Registration successful!")
                
                # Log successful registration
                logger.info(f"User registered successfully: {user.username}")
                
                return redirect('dashboard')
            except Exception as e:
                logger.error(f"Error during user registration: {str(e)}")
                messages.error(request, "An error occurred during registration. Please try again.")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'predictor/register.html', {'form': form})

@require_http_methods(["GET", "POST"])
def user_login(request):
    """User login view with improved security"""
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {username}!")
                
                # Log successful login
                logger.info(f"User logged in: {username}")
                
                # Get next parameter or redirect to dashboard
                next_url = request.GET.get('next', 'dashboard')
                return redirect(next_url)
            else:
                # Log failed login attempt
                logger.warning(f"Failed login attempt for username: {username}")
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = CustomAuthenticationForm()
    
    return render(request, 'predictor/login.html', {'form': form})

@login_required
def user_logout(request):
    """Explicit logout view"""
    username = request.user.username
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    
    # Log logout
    logger.info(f"User logged out: {username}")
    
    return redirect('home')

@login_required
def profile(request):
    """User profile view and edit with improved error handling"""
    try:
        user_profile, created = UserProfile.objects.get_or_create(user=request.user)
        
        if request.method == 'POST':
            form = UserProfileForm(request.POST, instance=user_profile)
            if form.is_valid():
                form.save()
                messages.success(request, "Profile updated successfully!")
                return redirect('profile')
        else:
            form = UserProfileForm(instance=user_profile)
        
        # Get the user's latest data for the profile page
        latest_risk = RiskAssessment.objects.filter(user=request.user).order_by('-date').first()
        latest_progress = ProgressTracking.objects.filter(user=request.user).order_by('-date').first()
        latest_prediction = DiabetesRiskPrediction.objects.filter(user=request.user).order_by('-date').first()
        
        context = {
            'form': form,
            'latest_risk': latest_risk,
            'latest_progress': latest_progress,
            'latest_prediction': latest_prediction,
        }
        
        return render(request, 'predictor/profile.html', context)
    except Exception as e:
        logger.error(f"Error in profile view: {str(e)}")
        messages.error(request, "An error occurred while accessing your profile. Please try again.")
        return redirect('dashboard')

@login_required
def dashboard(request):
    """User dashboard showing recent data and analytics with caching"""
    # Try to get cached dashboard data
    cache_key = f'dashboard_data_{request.user.id}'
    context = cache.get(cache_key)
    
    if context is None:
        try:
            # Get the user's latest data
            latest_risk = RiskAssessment.objects.filter(user=request.user).first()
            latest_lifestyle = LifestyleTracking.objects.filter(user=request.user).first()
            latest_progress = ProgressTracking.objects.filter(user=request.user).first()
            latest_prediction = DiabetesRiskPrediction.objects.filter(user=request.user).first()
            
            # For progress tracking, get data for the last month
            month_ago = timezone.now() - timedelta(days=30)
            progress_history = ProgressTracking.objects.filter(
                user=request.user, 
                date__gte=month_ago
            ).order_by('date')
            
            # Prepare progress data for charts
            dates = [entry.date.strftime('%Y-%m-%d') for entry in progress_history]
            weights = [entry.current_weight for entry in progress_history]
            fasting_sugars = [entry.fasting_blood_sugar for entry in progress_history if entry.fasting_blood_sugar]
            
            # Get aggregate statistics for insights
            all_progress = ProgressTracking.objects.filter(user=request.user)
            weight_stats = all_progress.aggregate(
                avg=Avg('current_weight'),
                max=Max('current_weight'),
                min=Min('current_weight')
            )
            
            all_risk_predictions = DiabetesRiskPrediction.objects.filter(user=request.user)
            risk_trend = [
                {
                    'date': pred.date.strftime('%Y-%m-%d'),
                    'probability': pred.probability
                } for pred in all_risk_predictions.order_by('date')[:5]
            ]
            
            context = {
                'latest_risk': latest_risk,
                'latest_lifestyle': latest_lifestyle,
                'latest_progress': latest_progress,
                'latest_prediction': latest_prediction,
                'dates': dates,
                'weights': weights,
                'fasting_sugars': fasting_sugars,
                'weight_stats': weight_stats,
                'risk_trend': risk_trend,
            }
            
            # Cache the result
            cache.set(cache_key, context, DASHBOARD_CACHE_TIMEOUT)
        except Exception as e:
            logger.error(f"Error in dashboard view: {str(e)}")
            messages.error(request, "An error occurred while loading your dashboard. Please try again.")
            context = {}
    
    return render(request, 'predictor/dashboard.html', context)

@require_http_methods(["GET", "POST"])
def predict(request):
    """Diabetes prediction view with improved validation and error handling"""
    prediction_result = None
    
    if request.method == 'POST':
        form = DiabetesPredictionForm(request.POST)
        if form.is_valid():
            try:
                # Get cleaned values from the form
                pregnancies = form.cleaned_data.get('pregnancies', 0)
                glucose = form.cleaned_data.get('glucose')
                blood_pressure = form.cleaned_data.get('blood_pressure')
                skin_thickness = form.cleaned_data.get('skin_thickness', 0)
                insulin = form.cleaned_data.get('insulin', 0)
                bmi = form.cleaned_data.get('bmi')
                diabetes_pedigree = form.cleaned_data.get('diabetes_pedigree')
                age = form.cleaned_data.get('age')

                # Input validation for numeric values
                if glucose <= 0 or blood_pressure <= 0 or bmi <= 0:
                    raise ValueError("Glucose, blood pressure, and BMI must be positive values")
                
                if age <= 0:
                    raise ValueError("Age must be greater than 0")
                
                # Load the model from cache
                model = get_prediction_model()

                # Make prediction
                features = np.array([[
                    pregnancies, glucose, blood_pressure, skin_thickness, 
                    insulin, bmi, diabetes_pedigree, age
                ]])
                prediction = bool(model.predict(features)[0])
                probability = float(model.predict_proba(features)[0][1] * 100)

                # Store result
                prediction_result = {
                    'prediction': prediction,
                    'probability': probability,
                    'features': {
                        'pregnancies': pregnancies,
                        'glucose': glucose,
                        'blood_pressure': blood_pressure,
                        'skin_thickness': skin_thickness,
                        'insulin': insulin,
                        'bmi': bmi,
                        'diabetes_pedigree': diabetes_pedigree,
                        'age': age
                    }
                }
                
                # Save prediction to database if user is logged in
                if request.user.is_authenticated:
                    DiabetesRiskPrediction.objects.create(
                        user=request.user,
                        pregnancies=pregnancies,
                        glucose=glucose,
                        blood_pressure=blood_pressure,
                        skin_thickness=skin_thickness,
                        insulin=insulin,
                        bmi=bmi,
                        diabetes_pedigree=diabetes_pedigree,
                        age=age,
                        prediction=prediction,
                        probability=probability
                    )
                    
                    # Invalidate dashboard cache
                    cache.delete(f'dashboard_data_{request.user.id}')
                
                # Return JSON response for AJAX calls
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': True,
                        'prediction': prediction,
                        'probability': probability
                    })
                
                # Log successful prediction
                logger.info(f"Prediction made: probability={probability:.1f}%, result={'positive' if prediction else 'negative'}")
                
            except ValueError as e:
                logger.warning(f"Validation error in prediction: {str(e)}")
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'error': str(e)
                    })
                messages.error(request, str(e))
            except Exception as e:
                logger.error(f"Error in prediction: {str(e)}")
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'error': "An error occurred during prediction. Please try again."
                    })
                messages.error(request, "An error occurred during prediction. Please try again.")
    else:
        form = DiabetesPredictionForm()
    
    context = {
        'form': form,
        'prediction_result': prediction_result
    }
    
    return render(request, 'predictor/predict.html', context)

def education(request):
    """Education page view"""
    return render(request, 'predictor/education.html')

def resources(request):
    """Resources page view"""
    return render(request, 'predictor/resources.html')

@login_required
@require_http_methods(["GET", "POST"])
def tracker(request):
    """Tracker page with forms for assessment, lifestyle, and progress tracking"""
    assessment_form = RiskAssessmentForm()
    lifestyle_form = LifestyleTrackingForm()
    progress_form = ProgressTrackingForm()
    
    if request.method == 'POST':
        try:
            if 'assessment_form' in request.POST:
                assessment_form = RiskAssessmentForm(request.POST)
                if assessment_form.is_valid():
                    assessment = assessment_form.save(commit=False)
                    assessment.user = request.user
                    assessment.save()
                    messages.success(request, "Risk assessment saved successfully!")
                    
                    # Invalidate dashboard cache
                    cache.delete(f'dashboard_data_{request.user.id}')
                    return redirect('tracker')
                
            elif 'lifestyle_form' in request.POST:
                lifestyle_form = LifestyleTrackingForm(request.POST)
                if lifestyle_form.is_valid():
                    lifestyle = lifestyle_form.save(commit=False)
                    lifestyle.user = request.user
                    lifestyle.save()
                    messages.success(request, "Lifestyle data saved successfully!")
                    
                    # Invalidate dashboard cache
                    cache.delete(f'dashboard_data_{request.user.id}')
                    return redirect('tracker')
                
            elif 'progress_form' in request.POST:
                progress_form = ProgressTrackingForm(request.POST)
                if progress_form.is_valid():
                    progress = progress_form.save(commit=False)
                    progress.user = request.user
                    progress.save()
                    messages.success(request, "Progress data saved successfully!")
                    
                    # Invalidate dashboard cache
                    cache.delete(f'dashboard_data_{request.user.id}')
                    return redirect('tracker')
        except Exception as e:
            logger.error(f"Error in tracker form submission: {str(e)}")
            messages.error(request, "An error occurred while saving your data. Please try again.")
    
    try:
        # Get recent entries for display
        recent_assessments = RiskAssessment.objects.filter(user=request.user).order_by('-date')[:3]
        recent_lifestyle = LifestyleTracking.objects.filter(user=request.user).order_by('-date')[:3]
        recent_progress = ProgressTracking.objects.filter(user=request.user).order_by('-date')[:3]
        
        context = {
            'assessment_form': assessment_form,
            'lifestyle_form': lifestyle_form,
            'progress_form': progress_form,
            'recent_assessments': recent_assessments,
            'recent_lifestyle': recent_lifestyle,
            'recent_progress': recent_progress
        }
    except Exception as e:
        logger.error(f"Error retrieving tracker data: {str(e)}")
        messages.error(request, "An error occurred while loading your tracking data. Please try again.")
        context = {
            'assessment_form': assessment_form,
            'lifestyle_form': lifestyle_form,
            'progress_form': progress_form,
        }
    
    return render(request, 'predictor/tracker.html', context)

@login_required
def history(request):
    """View for showing user's prediction and tracking history with pagination"""
    try:
        # Get parameter for type filtering
        history_type = request.GET.get('type', 'all')
        
        # Get page parameter for pagination
        page = int(request.GET.get('page', 1))
        per_page = 10
        start = (page - 1) * per_page
        end = start + per_page
        
        # Get all user history based on type filter
        risk_assessments = []
        lifestyle_entries = []
        progress_entries = []
        predictions = []
        
        if history_type in ['all', 'risk']:
            risk_assessments = RiskAssessment.objects.filter(user=request.user).order_by('-date')
        
        if history_type in ['all', 'lifestyle']:
            lifestyle_entries = LifestyleTracking.objects.filter(user=request.user).order_by('-date')
        
        if history_type in ['all', 'progress']:
            progress_entries = ProgressTracking.objects.filter(user=request.user).order_by('-date')
        
        if history_type in ['all', 'predictions']:
            predictions = DiabetesRiskPrediction.objects.filter(user=request.user).order_by('-date')
        
        # Count total entries
        total_count = len(risk_assessments) + len(lifestyle_entries) + len(progress_entries) + len(predictions)
        total_pages = (total_count + per_page - 1) // per_page
        
        context = {
            'risk_assessments': risk_assessments[start:end] if history_type in ['all', 'risk'] else [],
            'lifestyle_entries': lifestyle_entries[start:end] if history_type in ['all', 'lifestyle'] else [],
            'progress_entries': progress_entries[start:end] if history_type in ['all', 'progress'] else [],
            'predictions': predictions[start:end] if history_type in ['all', 'predictions'] else [],
            'history_type': history_type,
            'current_page': page,
            'total_pages': total_pages,
            'has_next': page < total_pages,
            'has_prev': page > 1,
            'next_page': page + 1,
            'prev_page': page - 1,
        }
    except Exception as e:
        logger.error(f"Error in history view: {str(e)}")
        messages.error(request, "An error occurred while loading your history. Please try again.")
        context = {}
    
    return render(request, 'predictor/history.html', context)

@csrf_exempt
@require_http_methods(["POST"])
def api_predict(request):
    """API endpoint for prediction with improved validation and security"""
    try:
        # Rate limiting check
        ip_address = get_client_ip(request)
        rate_limit_key = f'api_rate_limit_{ip_address}'
        request_count = cache.get(rate_limit_key, 0)
        
        if request_count >= 10:  # Maximum 10 requests per minute
            return JsonResponse({
                'success': False,
                'error': 'Rate limit exceeded. Please try again later.'
            }, status=429)
        
        # Increment request count
        cache.set(rate_limit_key, request_count + 1, 60)  # 1 minute expiry
        
        # Parse request data
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON data'
            }, status=400)
        
        # Input validation
        required_fields = ['glucose', 'blood_pressure', 'bmi', 'diabetes_pedigree', 'age']
        for field in required_fields:
            if field not in data:
                return JsonResponse({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }, status=400)
        
        # Get values from the request
        def safe_float(val, default=0):
            if val is None or val == '':
                return default
            try:
                return float(val)
            except (ValueError, TypeError):
                raise ValueError(f"Invalid value for {val}: must be a number")
        
        try:
            pregnancies = safe_float(data.get('pregnancies'), 0)
            glucose = safe_float(data.get('glucose'))
            blood_pressure = safe_float(data.get('blood_pressure'))
            skin_thickness = safe_float(data.get('skin_thickness'), 0)
            insulin = safe_float(data.get('insulin'), 0)
            bmi = safe_float(data.get('bmi'))
            diabetes_pedigree = safe_float(data.get('diabetes_pedigree'))
            age = safe_float(data.get('age'))
        except ValueError as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
        
        # Additional validation
        if glucose <= 0 or blood_pressure <= 0 or bmi <= 0 or age <= 0:
            return JsonResponse({
                'success': False,
                'error': 'Glucose, blood pressure, BMI, and age must be positive values'
            }, status=400)

        # Load the model from cache
        model = get_prediction_model()

        # Make prediction
        features = np.array([[
            pregnancies, glucose, blood_pressure, skin_thickness, 
            insulin, bmi, diabetes_pedigree, age
        ]])
        prediction = bool(model.predict(features)[0])
        probability = float(model.predict_proba(features)[0][1] * 100)

        # Log API request (anonymized)
        logger.info(f"API prediction made: probability={probability:.1f}%, result={'positive' if prediction else 'negative'}")
        
        return JsonResponse({
            'success': True,
            'prediction': prediction,
            'probability': probability,
            'risk_level': get_risk_level(probability)
        })
    
    except Exception as e:
        logger.error(f"API error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

def get_risk_level(probability):
    """Convert probability to risk level"""
    if probability < 20:
        return "Low"
    elif probability < 50:
        return "Moderate"
    elif probability < 70:
        return "High"
    else:
        return "Very High"

def get_client_ip(request):
    """Get client IP address"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

@login_required
def export_data(request, data_type):
    """Export user data in JSON format"""
    try:
        data = []
        
        if data_type == 'predictions':
            queryset = DiabetesRiskPrediction.objects.filter(user=request.user).order_by('-date')
            for item in queryset:
                data.append({
                    'date': item.date.strftime('%Y-%m-%d %H:%M:%S'),
                    'pregnancies': item.pregnancies,
                    'glucose': item.glucose,
                    'blood_pressure': item.blood_pressure,
                    'skin_thickness': item.skin_thickness,
                    'insulin': item.insulin,
                    'bmi': item.bmi,
                    'diabetes_pedigree': item.diabetes_pedigree,
                    'age': item.age,
                    'prediction': item.prediction,
                    'probability': item.probability
                })
        
        elif data_type == 'progress':
            queryset = ProgressTracking.objects.filter(user=request.user).order_by('-date')
            for item in queryset:
                data.append({
                    'date': item.date.strftime('%Y-%m-%d %H:%M:%S'),
                    'current_weight': item.current_weight,
                    'target_weight': item.target_weight,
                    'fasting_blood_sugar': item.fasting_blood_sugar,
                    'post_meal_blood_sugar': item.post_meal_blood_sugar
                })
        
        elif data_type == 'lifestyle':
            queryset = LifestyleTracking.objects.filter(user=request.user).order_by('-date')
            for item in queryset:
                data.append({
                    'date': item.date.strftime('%Y-%m-%d %H:%M:%S'),
                    'activity_level': item.activity_level,
                    'activity_type': item.get_activity_type_display(),
                    'meals_per_day': item.meals_per_day,
                    'diet_type': item.get_diet_type_display(),
                    'sleep_hours': item.sleep_hours,
                    'sleep_quality': item.get_sleep_quality_display()
                })
        
        elif data_type == 'risk_assessments':
            queryset = RiskAssessment.objects.filter(user=request.user).order_by('-date')
            for item in queryset:
                data.append({
                    'date': item.date.strftime('%Y-%m-%d %H:%M:%S'),
                    'age': item.age,
                    'bmi': item.bmi,
                    'blood_pressure': item.blood_pressure,
                    'family_history': item.family_history
                })
        
        else:
            return JsonResponse({
                'success': False,
                'error': 'Invalid data type'
            }, status=400)
            
        response = JsonResponse({
            'success': True,
            'data': data,
            'count': len(data),
            'user': request.user.username,
            'exported_at': timezone.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        
        response['Content-Disposition'] = f'attachment; filename="{data_type}_{request.user.username}.json"'
        return response
    
    except Exception as e:
        logger.error(f"Error exporting data: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'An error occurred while exporting data'
        }, status=500)
