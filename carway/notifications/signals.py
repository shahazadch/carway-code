from django.db.models.signals import post_save, post_init
from django.dispatch import receiver
from django.contrib.auth.models import User

from messaging.models import Message
from listings.models import CarListing
from .utils import create_message_notification, create_listing_update_notification
from .models import NotificationSetting

@receiver(post_save, sender=User)
def create_user_notification_settings(sender, instance, created, **kwargs):
    """
    Create notification settings for new users
    """
    if created:
        NotificationSetting.objects.create(user=instance)

@receiver(post_save, sender=Message)
def notify_message_recipient(sender, instance, created, **kwargs):
    """
    Notify a user when they receive a new message
    """
    if created:
        # Find the recipient (all participants except the sender)
        for user in instance.conversation.participants.all():
            if user != instance.sender:
                create_message_notification(
                    user=user,
                    sender=instance.sender,
                    conversation=instance.conversation
                )

# Store previous values for listing updates
_original_listing_values = {}

@receiver(post_init, sender=CarListing)
def store_original_listing_values(sender, instance, **kwargs):
    """
    Store original listing values when loaded from DB to detect changes later
    """
    # Save original values for this instance
    _original_listing_values[instance.pk] = {
        'price': instance.price,
        'mileage': instance.mileage,
        'description': instance.description,
    }

@receiver(post_save, sender=CarListing)
def notify_listing_update(sender, instance, created, **kwargs):
    """
    Notify interested users when a listing is updated
    """
    # Skip for new listings
    if created:
        return
    
    # Skip if we don't have the original values
    if instance.pk not in _original_listing_values:
        return
    
    # Check if important fields were updated
    original = _original_listing_values[instance.pk]
    price_changed = instance.price != original['price']
    mileage_changed = instance.mileage != original['mileage']
    description_changed = instance.description != original['description']
    
    # If any important field was updated, notify interested users
    if price_changed or mileage_changed or description_changed:
        # For a real implementation, we would have a model for tracking user interests
        # For now, let's just demonstrate with users who've messaged about this listing
        
        # Get all users who have conversations about this listing, except the owner
        interested_users = set()
        for conversation in instance.conversations.all():
            for user in conversation.participants.all():
                if user != instance.user:  # Skip the listing owner
                    interested_users.add(user)
        
        # Notify each interested user
        for user in interested_users:
            create_listing_update_notification(user=user, listing=instance)
    
    # Update the stored values for next time
    _original_listing_values[instance.pk] = {
        'price': instance.price,
        'mileage': instance.mileage,
        'description': instance.description,
    }