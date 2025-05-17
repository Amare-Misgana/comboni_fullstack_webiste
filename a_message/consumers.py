import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import Message
from common.models import UserProfile
from common.utility import get_room_name

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Get User objects first
        current_user = self.scope["user"]
        other_username = self.scope["url_route"]["kwargs"]["username"]
        
        if not current_user.is_authenticated:
            await self.close()
            return

        try:
            # Get UserProfile instances
            self.account_profile = await self.get_user_profile(current_user)
            self.other_profile = await self.get_user_profile_by_username(other_username)
        except UserProfile.DoesNotExist:
            await self.close()
            return

        self.room_name = get_room_name(current_user.username, other_username)

        await self.set_online(True)
        await self.channel_layer.group_add(self.room_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_name, self.channel_name)
        await self.set_online(False)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_content = data['message']
        
        # Save message and get timestamp
        message_obj = await self.save_message(message_content)
        
        await self.channel_layer.group_send(
            self.room_name,
            {
                'type': 'chat_message',
                'message': message_obj.message,
                'sender': self.scope["user"].username,
                'timestamp': message_obj.timestamp.isoformat()
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            "message": event["message"],
            "sender": event["sender"],
            "timestamp": event["timestamp"]
        }))

    @database_sync_to_async
    def get_user_profile(self, user):
        return UserProfile.objects.get(user=user)

    @database_sync_to_async
    def get_user_profile_by_username(self, username):
        user = User.objects.get(username=username)
        return UserProfile.objects.get(user=user)

    @database_sync_to_async
    def save_message(self, content):
        return Message.objects.create(
            sender=self.account_profile.user,
            receiver=self.other_profile.user,
            message=content
        )

    @database_sync_to_async
    def set_online(self, status):
        self.account_profile.online = status
        self.account_profile.save()