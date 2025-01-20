from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.db.models import Q, Max, Count
from .models import Message, ChatRoom
from django.utils import timezone

User = get_user_model()

@login_required
def chat_home(request):
    # Get all users except the current user
    users = User.objects.exclude(id=request.user.id).annotate(
        unread_count=Count(
            'sent_messages',
            filter=Q(sent_messages__receiver=request.user, sent_messages__is_read=False)
        ),
        last_message_time=Max(
            'sent_messages__timestamp',
            filter=Q(sent_messages__receiver=request.user) | Q(received_messages__sender=request.user)
        )
    ).order_by('-last_message_time', 'username')

    # Prepare user data with additional info
    users_data = []
    for user in users:
        users_data.append({
            'id': user.id,
            'username': user.username,
            'unread_count': user.unread_count,
            'last_message_time': user.last_message_time.isoformat() if user.last_message_time else None
        })

    return render(request, 'chat/chat.html', {
        'users': users,
        'users_json': users_data
    })

@login_required
def get_messages(request, user_id):
    other_user = get_object_or_404(User, id=user_id)
    
    # Get or create chat room for these users
    room_participants = [request.user.id, other_user.id]
    chat_room = ChatRoom.objects.filter(participants=request.user).filter(participants=other_user).first()
    
    if not chat_room:
        chat_room = ChatRoom.objects.create()
        chat_room.participants.add(request.user, other_user)
    
    # Get messages and mark unread ones as read
    messages = Message.objects.filter(
        Q(sender=request.user, receiver_id=user_id) |
        Q(sender_id=user_id, receiver=request.user)
    ).order_by('timestamp')
    
    # Mark messages as read
    messages.filter(receiver=request.user, is_read=False).update(
        is_read=True,
        chat_room=chat_room
    )
    
    messages_list = []
    for message in messages:
        messages_list.append({
            'id': message.id,
            'content': message.content,
            'sender_id': str(message.sender.id),
            'timestamp': message.timestamp.isoformat(),
            'is_read': message.is_read
        })
    
    # Update chat room's updated_at timestamp
    chat_room.updated_at = timezone.now()
    chat_room.save()
    
    return JsonResponse({
        'messages': messages_list,
        'chat_room_id': chat_room.id
    })

@login_required
def mark_messages_read(request, user_id):
    if request.method == 'POST':
        Message.objects.filter(
            sender_id=user_id,
            receiver=request.user,
            is_read=False
        ).update(is_read=True)
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def chat_room(request, room_name):
    
    return render(request, 'chat/room.html', {
        'room_name': room_name
    })
