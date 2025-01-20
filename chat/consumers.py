# chat/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import Message

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        if not self.user.is_authenticated:
            await self.close()
            return

        try:
            self.other_user_id = self.scope['url_route']['kwargs']['user_id']
            self.room_name = f"chat_{min(self.user.id, int(self.other_user_id))}_{max(self.user.id, int(self.other_user_id))}"
            self.room_group_name = f"chat_{self.room_name}"

            # Join room group
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            await self.accept()
        except Exception as e:
            print(f"WebSocket connect error: {str(e)}")
            await self.close()

    async def disconnect(self, close_code):
        try:
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
        except Exception as e:
            print(f"WebSocket disconnect error: {str(e)}")

    @database_sync_to_async
    def save_message(self, sender, recipient, content):
        try:
            return Message.objects.create(
                sender=sender,
                receiver=recipient,
                content=content,
                timestamp=timezone.now()
            )
        except Exception as e:
            print(f"Error saving message: {str(e)}")
            return None

    @database_sync_to_async
    def get_user(self, user_id):
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None
        except Exception as e:
            print(f"Error getting user: {str(e)}")
            return None

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            
            # Handle typing status
            if 'typing' in data:
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'typing_status',
                        'user_id': str(self.user.id),
                        'is_typing': data['typing']
                    }
                )
                return

            # Handle message
            message = data.get('message', '').strip()
            recipient_id = data.get('recipient_id')
            
            if not message or not recipient_id:
                return
            
            recipient = await self.get_user(recipient_id)
            if not recipient:
                return

            saved_message = await self.save_message(self.user, recipient, message)
            if not saved_message:
                return

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'sender_id': str(self.user.id),
                    'timestamp': saved_message.timestamp.isoformat()
                }
            )
        except json.JSONDecodeError:
            print("Invalid JSON received")
        except Exception as e:
            print(f"Error in receive: {str(e)}")

    async def typing_status(self, event):
        try:
            await self.send(text_data=json.dumps({
                'type': 'typing',
                'user_id': event['user_id'],
                'is_typing': event['is_typing']
            }))
        except Exception as e:
            print(f"Error in typing_status: {str(e)}")

    async def chat_message(self, event):
        try:
            await self.send(text_data=json.dumps({
                'type': 'message',
                'message': event['message'],
                'sender_id': event['sender_id'],
                'timestamp': event['timestamp']
            }))
        except Exception as e:
            print(f"Error in chat_message: {str(e)}")
