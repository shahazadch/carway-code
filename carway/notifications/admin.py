from django.contrib import admin
from .models import Notification, NotificationSetting

class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'notification_type', 'title', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('user__username', 'title', 'message')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at',)
    
    fieldsets = (
        (None, {
            'fields': ('user', 'notification_type', 'title', 'message', 'url', 'is_read')
        }),
        ('Content Object', {
            'fields': ('content_type', 'object_id'),
            'classes': ('collapse',),
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',),
        }),
    )

class NotificationSettingAdmin(admin.ModelAdmin):
    list_display = ('user', 'email_messages', 'email_listing_updates', 'email_listing_interest',
                   'onsite_messages', 'onsite_listing_updates', 'onsite_listing_interest')
    list_filter = ('email_messages', 'email_listing_updates', 'email_listing_interest',
                  'onsite_messages', 'onsite_listing_updates', 'onsite_listing_interest')
    search_fields = ('user__username',)
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Email Notifications', {
            'fields': ('email_messages', 'email_listing_updates', 'email_listing_interest')
        }),
        ('On-site Notifications', {
            'fields': ('onsite_messages', 'onsite_listing_updates', 'onsite_listing_interest')
        }),
    )

admin.site.register(Notification, NotificationAdmin)
admin.site.register(NotificationSetting, NotificationSettingAdmin)