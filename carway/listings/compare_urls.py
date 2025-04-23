from django.urls import path
from . import compare_views

urlpatterns = [
    path('', compare_views.comparison_dashboard, name='comparison_dashboard'),
    path('add/<int:listing_id>/', compare_views.add_to_comparison, name='add_to_comparison'),
    path('remove/<int:listing_id>/', compare_views.remove_from_comparison, name='remove_from_comparison'),
    path('clear/', compare_views.clear_comparison, name='clear_comparison'),
]