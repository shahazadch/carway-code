from django.urls import path
from . import views

urlpatterns = [
    path('inbox/', views.inbox, name='inbox'),
    path('conversation/<int:conversation_id>/', views.conversation_detail, name='conversation-detail'),
    path('conversation/new/<int:listing_id>/', views.new_conversation, name='new-conversation'),
    path('mark-as-read/<int:message_id>/', views.mark_as_read, name='mark-as-read'),
]
