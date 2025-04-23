"""
URL configuration for carway project.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from listings.models import CarListing, CarMake
from django.shortcuts import render
import datetime

def home_view(request):
    """Home page view that displays featured car listings."""
    featured_listings = CarListing.objects.all().order_by('-created_at')[:6]
    car_makes = CarMake.objects.all().order_by('name')
    current_year = datetime.date.today().year
    year_range = range(current_year, current_year - 30, -1)
    
    context = {
        'featured_listings': featured_listings,
        'car_makes': car_makes,
        'year_range': year_range,
    }
    
    # Using the EXACT theme template
    return render(request, 'theme_templates/home-cars.html', context)

def market_estimator_view(request):
    """
    Redirect to the estimator app home page.
    This is kept for backward compatibility with any existing links.
    """
    from django.shortcuts import redirect
    return redirect('estimator-home')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view, name='home'),
    path('users/', include('users.urls')),
    path('listings/', include('listings.urls')),
    path('messages/', include('messaging.urls')),
    path('estimator/', include('estimator.urls')),
    path('market-estimator/', market_estimator_view, name='market_estimator'),
    path('compare/', include('listings.compare_urls')),
    path('', include('notifications.urls')),  # Include notification URLs
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
