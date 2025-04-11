from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Public pages
    path('', views.home, name='home'),
    path('predict/', views.predict, name='predict'),
    path('education/', views.education, name='education'),
    path('resources/', views.resources, name='resources'),
    
    # Authentication
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    
    # User authenticated pages
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('tracker/', views.tracker, name='tracker'),
    path('history/', views.history, name='history'),
    
    # Data export
    path('export/<str:data_type>/', views.export_data, name='export_data'),
    
    # API endpoints
    path('api/predict/', views.api_predict, name='api_predict'),
] 