from django.db import models
from django.utils import timezone
import os
import pickle
import json
from listings.models import CarListing

class PriceModel(models.Model):
    """
    Model class for storing ML model metadata and the serialized model file.
    """
    MODEL_TYPES = [
        ('random_forest', 'Random Forest'),
        ('linear', 'Linear Regression'),
        ('gradient_boosting', 'Gradient Boosting'),
    ]
    
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    model_type = models.CharField(max_length=20, choices=MODEL_TYPES)
    model_data = models.BinaryField(null=True, blank=True)  # For storing serialized model
    feature_importance = models.JSONField(null=True, blank=True)  # For storing feature importance
    r_squared = models.FloatField(null=True, blank=True)
    mean_absolute_error = models.FloatField(null=True, blank=True)
    mean_squared_error = models.FloatField(null=True, blank=True)
    training_data_size = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.model_type}) - {self.created_at.strftime('%Y-%m-%d')}"
    
    def save(self, *args, **kwargs):
        # If this model is being set as active, deactivate all other models
        if self.is_active:
            PriceModel.objects.exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)
    
    @staticmethod
    def get_active_model():
        """Returns the currently active model"""
        try:
            return PriceModel.objects.filter(is_active=True).first()
        except PriceModel.DoesNotExist:
            return None
    
    def get_model_object(self):
        """Deserialize and return the actual ML model object"""
        if self.model_data:
            try:
                return pickle.loads(self.model_data)
            except Exception as e:
                print(f"Error loading model: {e}")
                return None
        return None
    
    def set_model_object(self, model_obj):
        """Serialize and store the ML model object"""
        try:
            self.model_data = pickle.dumps(model_obj)
            self.save()
            return True
        except Exception as e:
            print(f"Error saving model: {e}")
            return False


class PricePrediction(models.Model):
    """
    Model class for storing price predictions made by the system.
    """
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, null=True, blank=True)
    model = models.ForeignKey(PriceModel, on_delete=models.SET_NULL, null=True, blank=True)
    make = models.CharField(max_length=100)
    model_name = models.CharField(max_length=100)
    year = models.IntegerField()
    mileage = models.IntegerField()
    fuel_type = models.CharField(max_length=20)
    transmission = models.CharField(max_length=20)
    engine_size = models.CharField(max_length=10)
    body_type = models.CharField(max_length=20)
    color = models.CharField(max_length=20)
    predicted_price = models.DecimalField(max_digits=10, decimal_places=2)
    input_data = models.JSONField()  # Store all input parameters
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.year} {self.make} {self.model_name} - ${self.predicted_price}"