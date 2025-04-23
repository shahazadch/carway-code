from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

class Notification(models.Model):
    """
    Model for storing user notifications
    """
    NOTIFICATION_TYPES = (
        ('message', 'New Message'),
        ('listing_update', 'Listing Update'),
        ('listing_interest', 'Listing Interest'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=255)
    message = models.TextField()
    url = models.CharField(max_length=255, blank=True, null=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Generic foreign key to reference any model
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.get_notification_type_display()} for {self.user.username}"
    
    def mark_as_read(self):
        """Mark this notification as read"""
        self.is_read = True
        self.save()

class NotificationSetting(models.Model):
    """
    Model for user notification preferences
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notification_settings')
    
    # Email notification settings
    email_messages = models.BooleanField(default=True)
    email_listing_updates = models.BooleanField(default=True)
    email_listing_interest = models.BooleanField(default=True)
    
    # On-site notification settings
    onsite_messages = models.BooleanField(default=True)
    onsite_listing_updates = models.BooleanField(default=True)
    onsite_listing_interest = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Notification Settings for {self.user.username}"