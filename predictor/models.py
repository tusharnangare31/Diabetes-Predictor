from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    date_of_birth = models.DateField(null=True, blank=True)
    height_cm = models.FloatField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"

class RiskAssessment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='risk_assessments')
    date = models.DateTimeField(default=timezone.now)
    
    # Risk factors
    age = models.PositiveIntegerField()
    bmi = models.FloatField()
    blood_pressure = models.CharField(max_length=20)  # Stored as "systolic/diastolic"
    family_history = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-date']
    
    def __str__(self):
        return f"Assessment for {self.user.username} on {self.date.strftime('%Y-%m-%d')}"

class LifestyleTracking(models.Model):
    ACTIVITY_CHOICES = [
        ('walking', 'Walking'),
        ('running', 'Running'),
        ('cycling', 'Cycling'),
        ('swimming', 'Swimming'),
        ('strength', 'Strength Training'),
        ('other', 'Other'),
    ]
    
    DIET_CHOICES = [
        ('balanced', 'Balanced'),
        ('low_carb', 'Low Carb'),
        ('mediterranean', 'Mediterranean'),
        ('vegetarian', 'Vegetarian'),
        ('vegan', 'Vegan'),
        ('other', 'Other'),
    ]
    
    SLEEP_QUALITY_CHOICES = [
        ('excellent', 'Excellent'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lifestyle_tracking')
    date = models.DateTimeField(default=timezone.now)
    
    # Physical activity
    activity_level = models.PositiveIntegerField(help_text="Minutes per week")
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_CHOICES)
    
    # Diet
    meals_per_day = models.PositiveIntegerField()
    diet_type = models.CharField(max_length=20, choices=DIET_CHOICES)
    
    # Sleep
    sleep_hours = models.FloatField()
    sleep_quality = models.CharField(max_length=20, choices=SLEEP_QUALITY_CHOICES)
    
    class Meta:
        ordering = ['-date']
    
    def __str__(self):
        return f"Lifestyle data for {self.user.username} on {self.date.strftime('%Y-%m-%d')}"

class ProgressTracking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='progress_tracking')
    date = models.DateTimeField(default=timezone.now)
    
    # Weight tracking
    current_weight = models.FloatField(help_text="Weight in kg")
    target_weight = models.FloatField(help_text="Target weight in kg", null=True, blank=True)
    
    # Blood sugar tracking
    fasting_blood_sugar = models.FloatField(help_text="mg/dL", null=True, blank=True)
    post_meal_blood_sugar = models.FloatField(help_text="mg/dL", null=True, blank=True)
    
    class Meta:
        ordering = ['-date']
    
    def __str__(self):
        return f"Progress data for {self.user.username} on {self.date.strftime('%Y-%m-%d')}"
    
    def weight_progress_percentage(self):
        """Calculate weight progress percentage towards goal"""
        if not self.target_weight or self.current_weight == self.target_weight:
            return 0
        
        # For weight loss scenario
        if self.current_weight > self.target_weight:
            # Assuming starting weight is 10% higher than current
            starting_weight = self.current_weight * 1.1
            progress = ((starting_weight - self.current_weight) / 
                        (starting_weight - self.target_weight)) * 100
        # For weight gain scenario
        else:
            # Assuming starting weight is 10% lower than current
            starting_weight = self.current_weight * 0.9
            progress = ((self.current_weight - starting_weight) / 
                        (self.target_weight - starting_weight)) * 100
        
        # Limit to 0-100%
        return max(0, min(100, progress))

class DiabetesRiskPrediction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='risk_predictions')
    date = models.DateTimeField(default=timezone.now)
    
    # Risk factors
    pregnancies = models.PositiveIntegerField(default=0)
    glucose = models.FloatField()
    blood_pressure = models.FloatField()
    skin_thickness = models.FloatField()
    insulin = models.FloatField()
    bmi = models.FloatField()
    diabetes_pedigree = models.FloatField()
    age = models.PositiveIntegerField()
    
    # Prediction results
    prediction = models.BooleanField()
    probability = models.FloatField(help_text="Risk probability percentage")
    
    class Meta:
        ordering = ['-date']
    
    def __str__(self):
        risk_status = "High Risk" if self.prediction else "Low Risk"
        return f"{risk_status} prediction for {self.user.username} ({self.probability:.1f}%)"
