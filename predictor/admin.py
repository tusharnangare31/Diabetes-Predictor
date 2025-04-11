from django.contrib import admin
from .models import UserProfile, RiskAssessment, LifestyleTracking, ProgressTracking, DiabetesRiskPrediction

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'date_of_birth', 'height_cm')
    search_fields = ('user__username', 'user__email')

class RiskAssessmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'age', 'bmi', 'blood_pressure', 'family_history')
    list_filter = ('family_history', 'date')
    search_fields = ('user__username', 'user__email')
    date_hierarchy = 'date'

class LifestyleTrackingAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'activity_level', 'activity_type', 'diet_type', 'sleep_hours', 'sleep_quality')
    list_filter = ('activity_type', 'diet_type', 'sleep_quality', 'date')
    search_fields = ('user__username', 'user__email')
    date_hierarchy = 'date'

class ProgressTrackingAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'current_weight', 'target_weight', 'fasting_blood_sugar', 'post_meal_blood_sugar')
    list_filter = ('date',)
    search_fields = ('user__username', 'user__email')
    date_hierarchy = 'date'
    
    def get_weight_progress(self, obj):
        return f"{obj.weight_progress_percentage():.1f}%"
    get_weight_progress.short_description = "Weight Progress"

class DiabetesRiskPredictionAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'prediction', 'probability', 'glucose', 'bmi', 'age')
    list_filter = ('prediction', 'date')
    search_fields = ('user__username', 'user__email')
    date_hierarchy = 'date'

# Register models
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(RiskAssessment, RiskAssessmentAdmin)
admin.site.register(LifestyleTracking, LifestyleTrackingAdmin)
admin.site.register(ProgressTracking, ProgressTrackingAdmin)
admin.site.register(DiabetesRiskPrediction, DiabetesRiskPredictionAdmin)
