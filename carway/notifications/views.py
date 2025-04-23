from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseRedirect
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.core.paginator import Paginator

from .models import Notification, NotificationSetting

@login_required
def notification_list(request):
    """
    View for displaying user notifications
    """
    notifications = request.user.notifications.all()
    unread_count = notifications.filter(is_read=False).count()
    
    # Pagination
    paginator = Paginator(notifications, 10)  # Show 10 notifications per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'theme_templates/notifications/notification_list.html', {
        'page_obj': page_obj,
        'unread_count': unread_count,
    })

@login_required
@require_POST
def mark_all_as_read(request):
    """
    Mark all notifications as read
    """
    request.user.notifications.filter(is_read=False).update(is_read=True)
    messages.success(request, 'All notifications marked as read')
    
    # Redirect back to referrer or notification list
    next_url = request.META.get('HTTP_REFERER')
    if next_url:
        return HttpResponseRedirect(next_url)
    return redirect('notification-list')

@login_required
def mark_as_read(request, notification_id):
    """
    Mark a single notification as read and redirect to its URL if available
    """
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    
    # Redirect to the notification URL if it exists, otherwise back to list
    if notification.url:
        return redirect(notification.url)
    
    # Redirect back to referrer or notification list
    next_url = request.META.get('HTTP_REFERER')
    if next_url:
        return HttpResponseRedirect(next_url)
    return redirect('notification-list')

@login_required
def notification_settings(request):
    """
    View for managing notification settings
    """
    # Get or create notification settings for the user
    settings, created = NotificationSetting.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        # Update email notification settings
        settings.email_messages = 'email_messages' in request.POST
        settings.email_listing_updates = 'email_listing_updates' in request.POST
        settings.email_listing_interest = 'email_listing_interest' in request.POST
        
        # Update on-site notification settings
        settings.onsite_messages = 'onsite_messages' in request.POST
        settings.onsite_listing_updates = 'onsite_listing_updates' in request.POST
        settings.onsite_listing_interest = 'onsite_listing_interest' in request.POST
        
        # Save changes
        settings.save()
        
        messages.success(request, 'Notification settings updated successfully')
        return redirect('notification-settings')
    
    return render(request, 'theme_templates/notifications/notification_settings.html', {
        'settings': settings,
    })

@login_required
def unread_count(request):
    """
    Returns the count of unread notifications as JSON
    Used for real-time updates via AJAX
    """
    count = request.user.notifications.filter(is_read=False).count()
    return JsonResponse({'count': count})