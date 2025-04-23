from django.contrib import admin
from .models import CarListing, CarImage, CarMake, CarModel

admin.site.register(CarListing)
admin.site.register(CarImage)
admin.site.register(CarMake)
admin.site.register(CarModel)
