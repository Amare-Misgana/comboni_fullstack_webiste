import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from common.models import UserProfile
from .models import Message

logger = logging.getLogger(__name__)

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        self.room_name = self.scope["url_route"]["kwargs"]["roomname"]

        if not self.user.is_authenticated:
            await self.close()
            return

        await self.channel_layer.group_add(
            self.room_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_name, self.channel_name)


    async def receive(self, text_data):
        data = json.loads(text_data)

        try:
            message_obj = await self.save_message(data)
        except Exception as e:
            logger.error(f"Error saving message: {e}")
            return

        await self.channel_layer.group_send(
            self.room_name,
            {
                'type': 'chat_message',
                'message': message_obj.message,
                'receiver': message_obj.receiver.username,
                'sender': self.user.username,
                'timestamp': message_obj.timestamp.isoformat()
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            "message": event["message"],
            "sender": event["sender"],
            "receiver": event["receiver"],
            "timestamp": event["timestamp"]
        }))

    @database_sync_to_async
    def save_message(self, content):
        try: 
            receiver = UserProfile.objects.get(user__username=content["receiver"])
        except Exception as e:
            logger.error(f"Error in quering receiver: {e}")
        try:
            sender = UserProfile.objects.get(user__username=self.user)
        except Exception as e:
            logger.error(f"Error in quering sender: {e}")
        return Message.objects.create(
            sender=sender,
            receiver=receiver,
            message=content["message"]
        )

class OnlineStatus(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]

        if not self.user.is_authenticated:
            await self.close()
            return

        self.room_name = "online_status"  # static group for all users
        await self.channel_layer.group_add(
            self.room_name,
            self.channel_name
        )
        await self.accept()

        await self.set_online(True)

        await self.channel_layer.group_send(
            self.room_name,
            {
                'type': 'user_status',
                'user': self.user.username,
                'status': 'online'
            }
        )

    async def disconnect(self, close_code):
        await self.set_online(False)

        await self.channel_layer.group_send(
            self.room_name,
            {
                'type': 'user_status',
                'user': self.user.username,
                'status': 'offline'
            }
        )

        await self.channel_layer.group_discard(self.room_name, self.channel_name)

    async def user_status(self, event):
        await self.send(text_data=json.dumps({
            "type": "status",
            "user": event["user"],
            "status": event["status"]
        }))

    @database_sync_to_async
    def set_online(self, status):
        self.user.online = status
        self.user.save()
