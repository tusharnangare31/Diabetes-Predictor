# Generated by Django 5.2 on 2025-04-11 08:22

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='DiabetesRiskPrediction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
                ('pregnancies', models.PositiveIntegerField(default=0)),
                ('glucose', models.FloatField()),
                ('blood_pressure', models.FloatField()),
                ('skin_thickness', models.FloatField()),
                ('insulin', models.FloatField()),
                ('bmi', models.FloatField()),
                ('diabetes_pedigree', models.FloatField()),
                ('age', models.PositiveIntegerField()),
                ('prediction', models.BooleanField()),
                ('probability', models.FloatField(help_text='Risk probability percentage')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='risk_predictions', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-date'],
            },
        ),
        migrations.CreateModel(
            name='LifestyleTracking',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
                ('activity_level', models.PositiveIntegerField(help_text='Minutes per week')),
                ('activity_type', models.CharField(choices=[('walking', 'Walking'), ('running', 'Running'), ('cycling', 'Cycling'), ('swimming', 'Swimming'), ('strength', 'Strength Training'), ('other', 'Other')], max_length=20)),
                ('meals_per_day', models.PositiveIntegerField()),
                ('diet_type', models.CharField(choices=[('balanced', 'Balanced'), ('low_carb', 'Low Carb'), ('mediterranean', 'Mediterranean'), ('vegetarian', 'Vegetarian'), ('vegan', 'Vegan'), ('other', 'Other')], max_length=20)),
                ('sleep_hours', models.FloatField()),
                ('sleep_quality', models.CharField(choices=[('excellent', 'Excellent'), ('good', 'Good'), ('fair', 'Fair'), ('poor', 'Poor')], max_length=20)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lifestyle_tracking', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-date'],
            },
        ),
        migrations.CreateModel(
            name='ProgressTracking',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
                ('current_weight', models.FloatField(help_text='Weight in kg')),
                ('target_weight', models.FloatField(blank=True, help_text='Target weight in kg', null=True)),
                ('fasting_blood_sugar', models.FloatField(blank=True, help_text='mg/dL', null=True)),
                ('post_meal_blood_sugar', models.FloatField(blank=True, help_text='mg/dL', null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='progress_tracking', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-date'],
            },
        ),
        migrations.CreateModel(
            name='RiskAssessment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
                ('age', models.PositiveIntegerField()),
                ('bmi', models.FloatField()),
                ('blood_pressure', models.CharField(max_length=20)),
                ('family_history', models.BooleanField(default=False)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='risk_assessments', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-date'],
            },
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_of_birth', models.DateField(blank=True, null=True)),
                ('height_cm', models.FloatField(blank=True, null=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
