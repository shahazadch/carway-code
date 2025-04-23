from django.contrib import admin
from .models import PriceModel, PricePrediction

@admin.register(PriceModel)
class PriceModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'model_type', 'is_active', 'r_squared', 'created_at')
    list_filter = ('model_type', 'is_active')
    search_fields = ('name', 'description')
    ordering = ('-created_at',)

@admin.register(PricePrediction)
class PricePredictionAdmin(admin.ModelAdmin):
    list_display = ('make', 'model_name', 'year', 'mileage', 'predicted_price', 'created_at')
    list_filter = ('make', 'fuel_type', 'transmission', 'body_type')
    search_fields = ('make', 'model_name')
    ordering = ('-created_at',)