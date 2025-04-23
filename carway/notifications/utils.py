from django.contrib.contenttypes.models import ContentType
from django.urls import reverse

from .models import Notification, NotificationSetting

def create_notification(user, notification_type, title, message, url=None, content_object=None):
    """
    Create a notification for a user
    
    Args:
        user: User object - the user to notify
        notification_type: str - type of notification (message, listing_update, listing_interest)
        title: str - notification title
        message: str - notification message
        url: str - optional URL to redirect to when clicking the notification
        content_object: Model instance - optional related object for the notification
    
    Returns:
        Notification object
    """
    # Check if user has notification settings
    settings, created = NotificationSetting.objects.get_or_create(user=user)
    
    # Check if user wants this type of notification (on-site)
    if notification_type == 'message' and not settings.onsite_messages:
        return None
    elif notification_type == 'listing_update' and not settings.onsite_listing_updates:
        return None
    elif notification_type == 'listing_interest' and not settings.onsite_listing_interest:
        return None
    
    # Create notification
    notification = Notification(
        user=user,
        notification_type=notification_type,
        title=title,
        message=message,
        url=url
    )
    
    # If content_object is provided, set the generic relation
    if content_object:
        notification.content_type = ContentType.objects.get_for_model(content_object)
        notification.object_id = content_object.id
    
    notification.save()
    return notification

def create_message_notification(user, sender, conversation):
    """
    Create a notification for a new message
    
    Args:
        user: User object - the user to notify
        sender: User object - the user who sent the message
        conversation: Conversation object - the conversation containing the message
    
    Returns:
        Notification object
    """
    title = f"New message from {sender.username}"
    message = f"{sender.username} sent you a message about '{conversation.listing.make} {conversation.listing.model}'."
    url = reverse('conversation-detail', args=[conversation.id])
    
    return create_notification(
        user=user,
        notification_type='message',
        title=title,
        message=message,
        url=url,
        content_object=conversation
    )

def create_listing_update_notification(user, listing):
    """
    Create a notification for a listing update
    
    Args:
        user: User object - the user to notify
        listing: CarListing object - the updated listing
    
    Returns:
        Notification object
    """
    title = f"Listing updated: {listing.make} {listing.model}"
    message = f"A listing you're interested in has been updated: {listing.year} {listing.make} {listing.model}."
    url = reverse('listing-detail', args=[listing.id])
    
    return create_notification(
        user=user,
        notification_type='listing_update',
        title=title,
        message=message,
        url=url,
        content_object=listing
    )

def create_listing_interest_notification(user, interested_user, listing):
    """
    Create a notification for interest in a user's listing
    
    Args:
        user: User object - the user to notify (listing owner)
        interested_user: User object - the user who showed interest
        listing: CarListing object - the listing of interest
    
    Returns:
        Notification object
    """
    title = f"Interest in your listing"
    message = f"{interested_user.username} is interested in your {listing.year} {listing.make} {listing.model}."
    url = reverse('listing-detail', args=[listing.id])
    
    return create_notification(
        user=user,
        notification_type='listing_interest',
        title=title,
        message=message,
        url=url,
        content_object=listing
    )