from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Max, Count
from .models import Conversation, Message
from .forms import MessageForm
from listings.models import CarListing


@login_required
def inbox(request):
    conversations = Conversation.objects.filter(participants=request.user).annotate(
        last_message_time=Max('messages__created_at'),
        unread_count=Count('messages', filter=Q(messages__is_read=False) & ~Q(messages__sender=request.user))
    ).order_by('-last_message_time')
    
    return render(request, 'messaging/inbox.html', {'conversations': conversations})


@login_required
def conversation_detail(request, conversation_id):
    conversation = get_object_or_404(
        Conversation, 
        id=conversation_id, 
        participants=request.user
    )
    
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.conversation = conversation
            message.sender = request.user
            message.save()
            
            conversation.updated_at = message.created_at
            conversation.save()
            
            return redirect('conversation-detail', conversation_id=conversation.id)
    else:
        form = MessageForm()
    
    # Mark messages as read
    unread_messages = conversation.messages.filter(is_read=False).exclude(sender=request.user)
    for message in unread_messages:
        message.is_read = True
        message.save()
    
    messages_list = conversation.messages.all()
    
    return render(request, 'messaging/conversation.html', {
        'conversation': conversation,
        'messages': messages_list,
        'form': form
    })


@login_required
def new_conversation(request, listing_id):
    listing = get_object_or_404(CarListing, id=listing_id)
    
    # Check if a conversation about this listing already exists between these users
    existing_conversation = Conversation.objects.filter(
        participants=request.user,
        listing=listing
    ).filter(
        participants=listing.user
    )
    
    if existing_conversation.exists():
        return redirect('conversation-detail', conversation_id=existing_conversation.first().id)
    
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            # Create new conversation
            conversation = Conversation.objects.create(listing=listing)
            conversation.participants.add(request.user, listing.user)
            
            # Create first message
            message = form.save(commit=False)
            message.conversation = conversation
            message.sender = request.user
            message.save()
            
            messages.success(request, 'Your message has been sent!')
            return redirect('conversation-detail', conversation_id=conversation.id)
    else:
        form = MessageForm()
    
    return render(request, 'messaging/message_form.html', {
        'form': form,
        'listing': listing
    })


@login_required
def mark_as_read(request, message_id):
    message = get_object_or_404(Message, id=message_id)
    
    # Check if the user is part of the conversation
    if request.user in message.conversation.participants.all():
        message.is_read = True
        message.save()
        return JsonResponse({'status': 'success'})
    
    return JsonResponse({'status': 'error'}, status=403)
