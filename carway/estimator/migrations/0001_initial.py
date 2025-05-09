# Generated by Django 5.2 on 2025-04-22 15:58

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='PriceModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('model_file', models.FileField(upload_to='ml_models/')),
                ('is_active', models.BooleanField(default=False)),
                ('r_squared', models.FloatField(blank=True, null=True)),
                ('mean_absolute_error', models.FloatField(blank=True, null=True)),
                ('mean_squared_error', models.FloatField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='PricePrediction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('make', models.CharField(max_length=50)),
                ('model', models.CharField(max_length=50)),
                ('year', models.IntegerField()),
                ('mileage', models.IntegerField()),
                ('fuel_type', models.CharField(max_length=20)),
                ('transmission', models.CharField(max_length=20)),
                ('engine_size', models.CharField(max_length=10)),
                ('body_type', models.CharField(max_length=20)),
                ('color', models.CharField(max_length=20)),
                ('predicted_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('model_version', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='estimator.pricemodel')),
            ],
        ),
    ]
