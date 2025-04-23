from django.urls import path
from . import views

urlpatterns = [
    path('notifications/', views.notification_list, name='notification-list'),
    path('notifications/settings/', views.notification_settings, name='notification-settings'),
    path('notifications/mark-all-read/', views.mark_all_as_read, name='notification-mark-all-read'),
    path('notifications/mark-read/<int:notification_id>/', views.mark_as_read, name='notification-mark-read'),
    path('notifications/unread-count/', views.unread_count, name='notification-unread-count'),
]