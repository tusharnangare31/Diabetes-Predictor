from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import UserProfile, RiskAssessment, LifestyleTracking, ProgressTracking, DiabetesRiskPrediction

class CustomUserCreationForm(UserCreationForm):
    """Extended user registration form with email field"""
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
            # Create user profile
            UserProfile.objects.create(user=user)
        return user

class CustomAuthenticationForm(AuthenticationForm):
    """Custom authentication form with styled fields"""
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'class': 'shadow-sm focus:ring-blue-500 focus:border-blue-500 block w-full sm:text-sm border-gray-300 rounded-md',
                'placeholder': 'Username',
                'autocomplete': 'username',
            }
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'class': 'shadow-sm focus:ring-blue-500 focus:border-blue-500 block w-full sm:text-sm border-gray-300 rounded-md',
                'placeholder': 'Password',
                'autocomplete': 'current-password',
            }
        )
    )

class UserProfileForm(forms.ModelForm):
    """Form for updating UserProfile"""
    date_of_birth = forms.DateField(
        required=False,
        widget=forms.DateInput(
            attrs={
                'type': 'date',
                'class': 'shadow-sm focus:ring-blue-500 focus:border-blue-500 block w-full sm:text-sm border-gray-300 rounded-md pl-10',
                'placeholder': 'YYYY-MM-DD',
            }
        )
    )
    
    height_cm = forms.FloatField(
        required=False,
        widget=forms.NumberInput(
            attrs={
                'class': 'shadow-sm focus:ring-blue-500 focus:border-blue-500 block w-full sm:text-sm border-gray-300 rounded-md pl-10',
                'placeholder': 'Height in cm',
                'step': '0.1',
                'min': '50',
                'max': '250',
            }
        )
    )
    
    class Meta:
        model = UserProfile
        fields = ['date_of_birth', 'height_cm']

class RiskAssessmentForm(forms.ModelForm):
    """Form for Risk Assessment data entry"""
    class Meta:
        model = RiskAssessment
        exclude = ['user', 'date']
        widgets = {
            'age': forms.NumberInput(attrs={'class': 'shadow-sm focus:ring-blue-500 focus:border-blue-500 block w-full sm:text-sm border-gray-300 rounded-md', 'min': '1', 'max': '120'}),
            'bmi': forms.NumberInput(attrs={'class': 'shadow-sm focus:ring-blue-500 focus:border-blue-500 block w-full sm:text-sm border-gray-300 rounded-md', 'step': '0.1', 'min': '10', 'max': '50'}),
            'blood_pressure': forms.TextInput(attrs={'class': 'shadow-sm focus:ring-blue-500 focus:border-blue-500 block w-full sm:text-sm border-gray-300 rounded-md', 'placeholder': 'e.g. 120/80'}),
            'family_history': forms.CheckboxInput(attrs={'class': 'h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded'}),
        }

class LifestyleTrackingForm(forms.ModelForm):
    """Form for Lifestyle Tracking data entry"""
    class Meta:
        model = LifestyleTracking
        exclude = ['user', 'date']
        widgets = {
            'activity_level': forms.NumberInput(attrs={'class': 'shadow-sm focus:ring-blue-500 focus:border-blue-500 block w-full sm:text-sm border-gray-300 rounded-md', 'min': '0', 'max': '1000'}),
            'activity_type': forms.Select(attrs={'class': 'shadow-sm focus:ring-blue-500 focus:border-blue-500 block w-full sm:text-sm border-gray-300 rounded-md'}),
            'meals_per_day': forms.NumberInput(attrs={'class': 'shadow-sm focus:ring-blue-500 focus:border-blue-500 block w-full sm:text-sm border-gray-300 rounded-md', 'min': '1', 'max': '10'}),
            'diet_type': forms.Select(attrs={'class': 'shadow-sm focus:ring-blue-500 focus:border-blue-500 block w-full sm:text-sm border-gray-300 rounded-md'}),
            'sleep_hours': forms.NumberInput(attrs={'class': 'shadow-sm focus:ring-blue-500 focus:border-blue-500 block w-full sm:text-sm border-gray-300 rounded-md', 'step': '0.5', 'min': '0', 'max': '24'}),
            'sleep_quality': forms.Select(attrs={'class': 'shadow-sm focus:ring-blue-500 focus:border-blue-500 block w-full sm:text-sm border-gray-300 rounded-md'}),
        }

class ProgressTrackingForm(forms.ModelForm):
    """Form for Progress Tracking data entry"""
    class Meta:
        model = ProgressTracking
        exclude = ['user', 'date']
        widgets = {
            'current_weight': forms.NumberInput(attrs={'class': 'shadow-sm focus:ring-blue-500 focus:border-blue-500 block w-full sm:text-sm border-gray-300 rounded-md', 'step': '0.1', 'min': '20', 'max': '250'}),
            'target_weight': forms.NumberInput(attrs={'class': 'shadow-sm focus:ring-blue-500 focus:border-blue-500 block w-full sm:text-sm border-gray-300 rounded-md', 'step': '0.1', 'min': '20', 'max': '250'}),
            'fasting_blood_sugar': forms.NumberInput(attrs={'class': 'shadow-sm focus:ring-blue-500 focus:border-blue-500 block w-full sm:text-sm border-gray-300 rounded-md', 'min': '50', 'max': '500'}),
            'post_meal_blood_sugar': forms.NumberInput(attrs={'class': 'shadow-sm focus:ring-blue-500 focus:border-blue-500 block w-full sm:text-sm border-gray-300 rounded-md', 'min': '50', 'max': '500'}),
        }

class DiabetesPredictionForm(forms.ModelForm):
    """Form for Diabetes Prediction"""
    class Meta:
        model = DiabetesRiskPrediction
        exclude = ['user', 'date', 'prediction', 'probability']
        widgets = {
            'pregnancies': forms.NumberInput(attrs={'class': 'shadow-sm focus:ring-blue-500 focus:border-blue-500 block w-full sm:text-sm border-gray-300 rounded-md', 'min': '0', 'max': '20'}),
            'glucose': forms.NumberInput(attrs={'class': 'shadow-sm focus:ring-blue-500 focus:border-blue-500 block w-full sm:text-sm border-gray-300 rounded-md', 'min': '50', 'max': '300'}),
            'blood_pressure': forms.NumberInput(attrs={'class': 'shadow-sm focus:ring-blue-500 focus:border-blue-500 block w-full sm:text-sm border-gray-300 rounded-md', 'min': '40', 'max': '200'}),
            'skin_thickness': forms.NumberInput(attrs={'class': 'shadow-sm focus:ring-blue-500 focus:border-blue-500 block w-full sm:text-sm border-gray-300 rounded-md', 'min': '0', 'max': '100'}),
            'insulin': forms.NumberInput(attrs={'class': 'shadow-sm focus:ring-blue-500 focus:border-blue-500 block w-full sm:text-sm border-gray-300 rounded-md', 'min': '0', 'max': '1000'}),
            'bmi': forms.NumberInput(attrs={'class': 'shadow-sm focus:ring-blue-500 focus:border-blue-500 block w-full sm:text-sm border-gray-300 rounded-md', 'step': '0.1', 'min': '10', 'max': '50'}),
            'diabetes_pedigree': forms.NumberInput(attrs={'class': 'shadow-sm focus:ring-blue-500 focus:border-blue-500 block w-full sm:text-sm border-gray-300 rounded-md', 'step': '0.001', 'min': '0', 'max': '3'}),
            'age': forms.NumberInput(attrs={'class': 'shadow-sm focus:ring-blue-500 focus:border-blue-500 block w-full sm:text-sm border-gray-300 rounded-md', 'min': '1', 'max': '120'}),
        } 