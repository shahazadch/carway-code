from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class CarMake(models.Model):
    name = models.CharField(max_length=50)
    
    def __str__(self):
        return self.name


class CarModel(models.Model):
    make = models.ForeignKey(CarMake, on_delete=models.CASCADE, related_name='models')
    name = models.CharField(max_length=50)
    
    def __str__(self):
        return f"{self.make.name} {self.name}"


class CarListing(models.Model):
    FUEL_CHOICES = [
        ('Petrol', 'Petrol'),
        ('Diesel', 'Diesel'),
        ('Electric', 'Electric'),
        ('Hybrid', 'Hybrid'),
        ('LPG', 'LPG'),
        ('Other', 'Other'),
    ]
    
    TRANSMISSION_CHOICES = [
        ('Manual', 'Manual'),
        ('Automatic', 'Automatic'),
        ('Semi-Automatic', 'Semi-Automatic'),
        ('Other', 'Other'),
    ]
    
    BODY_CHOICES = [
        ('Sedan', 'Sedan'),
        ('SUV', 'SUV'),
        ('Hatchback', 'Hatchback'),
        ('Coupe', 'Coupe'),
        ('Convertible', 'Convertible'),
        ('Wagon', 'Wagon'),
        ('Van', 'Van'),
        ('Truck', 'Truck'),
        ('Other', 'Other'),
    ]
    
    COLOR_CHOICES = [
        ('Black', 'Black'),
        ('White', 'White'),
        ('Silver', 'Silver'),
        ('Gray', 'Gray'),
        ('Red', 'Red'),
        ('Blue', 'Blue'),
        ('Green', 'Green'),
        ('Yellow', 'Yellow'),
        ('Orange', 'Orange'),
        ('Brown', 'Brown'),
        ('Purple', 'Purple'),
        ('Gold', 'Gold'),
        ('Other', 'Other'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    make = models.ForeignKey(CarMake, on_delete=models.CASCADE)
    model = models.ForeignKey(CarModel, on_delete=models.CASCADE)
    year = models.IntegerField()
    mileage = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    fuel_type = models.CharField(max_length=20, choices=FUEL_CHOICES)
    transmission = models.CharField(max_length=20, choices=TRANSMISSION_CHOICES)
    engine_size = models.CharField(max_length=10)
    body_type = models.CharField(max_length=20, choices=BODY_CHOICES)
    color = models.CharField(max_length=20, choices=COLOR_CHOICES)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.year} {self.make} {self.model} - ${self.price}"
    
    def get_absolute_url(self):
        return reverse('listing-detail', kwargs={'pk': self.pk})
    
    def get_main_image(self):
        images = self.images.all()
        if images.exists():
            return images.first().image.url
        return None


class CarImage(models.Model):
    car_listing = models.ForeignKey(CarListing, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='car_images')
    
    def __str__(self):
        return f"Image for {self.car_listing}"
