from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from .models import CarListing

def comparison_dashboard(request):
    """Display the car comparison dashboard with all selected cars."""
    # Get comparison list from session or initialize empty
    comparison_list = request.session.get('comparison_list', [])
    
    # Get all listings in the comparison list
    listings = CarListing.objects.filter(id__in=comparison_list)
    
    # Get year range for context
    current_year = 2023  # Using a fixed year for predictability
    year_range = range(current_year, current_year - 20, -1)
    
    # Create context data for the template
    context = {
        'listings': listings,
        'comparison_count': len(comparison_list),
        'year_range': year_range,
    }
    
    return render(request, 'listings/comparison_dashboard.html', context)

def add_to_comparison(request, listing_id):
    """Add a car to the comparison list."""
    # Get the listing
    listing = get_object_or_404(CarListing, id=listing_id)
    
    # Get current comparison list
    comparison_list = request.session.get('comparison_list', [])
    
    # Check if this listing is already in the comparison
    if listing_id in comparison_list:
        messages.warning(request, f'{listing.make.name} {listing.model.name} is already in your comparison list.')
        return redirect('comparison_dashboard')
    
    # Limit comparison to 4 cars
    if len(comparison_list) >= 4:
        messages.warning(request, 'You can compare a maximum of 4 cars at a time.')
        return redirect('comparison_dashboard')
    
    # Add listing to comparison list
    comparison_list.append(listing_id)
    request.session['comparison_list'] = comparison_list
    
    messages.success(request, f'{listing.make.name} {listing.model.name} added to comparison.')
    
    # If this is an AJAX request, return JSON response
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success', 'count': len(comparison_list)})
    
    # Otherwise redirect to the referring page or the comparison dashboard
    referer = request.META.get('HTTP_REFERER')
    if referer:
        return redirect(referer)
    
    return redirect('comparison_dashboard')

def remove_from_comparison(request, listing_id):
    """Remove a car from the comparison list."""
    # Get current comparison list
    comparison_list = request.session.get('comparison_list', [])
    
    # Remove listing from comparison if it exists
    if listing_id in comparison_list:
        comparison_list.remove(listing_id)
        request.session['comparison_list'] = comparison_list
        
        # Get listing for the message
        listing = get_object_or_404(CarListing, id=listing_id)
        messages.success(request, f'{listing.make.name} {listing.model.name} removed from comparison.')
    
    # If this is an AJAX request, return JSON response
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success', 'count': len(comparison_list)})
    
    return redirect('comparison_dashboard')

def clear_comparison(request):
    """Clear all cars from the comparison list."""
    # Clear comparison list
    request.session['comparison_list'] = []
    
    messages.success(request, 'Comparison list cleared.')
    
    # If this is an AJAX request, return JSON response
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success', 'count': 0})
    
    return redirect('comparison_dashboard')