from channels.generic.websocket import WebsocketConsumer
from django.shortcuts import get_object_or_404
from asgiref.sync import async_to_sync
from .models import ChatGroup, GroupMessage
from django.contrib.auth.models import User
import json

class ChatroomConsumer(WebsocketConsumer):
    
    def connect(self):
        self.user = self.scope['user']
        self.chatroom_name = self.scope['url_route']['kwargs']['chatroom_name']
        self.chatroom = get_object_or_404(ChatGroup, group_name=self.chatroom_name)

        print(f"[CONNECT] User: {self.user} trying to connect to chatroom: {self.chatroom_name}")

        # Commented out the private access restriction for testing
        # if self.chatroom.is_private and self.user not in self.chatroom.members.all():
        #     print(f"[CONNECT] User {self.user} not allowed in private chatroom {self.chatroom_name}. Closing connection.")
        #     self.close()
        #     return

        async_to_sync(self.channel_layer.group_add)(
            self.chatroom_name,
            self.channel_name
        )

        self.accept()
        print(f"[CONNECT] Connection accepted for user {self.user} in chatroom {self.chatroom_name}")

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.chatroom_name,
            self.channel_name
        )
        print(f"[DISCONNECT] User {self.user} disconnected from chatroom {self.chatroom_name}")

        # if self.user in self.chatroom.users_online.all():
        #     self.chatroom.users_online.remove(self.user)
        #     self.update_online_count()
        #     print(f"[DISCONNECT] Removed {self.user} from online users in {self.chatroom_name}")

    def receive(self, text_data):
        print(f"[RECEIVE] Raw data from user {self.user}: {text_data}")
        data = json.loads(text_data)
        body = data.get('body')

        if self.user.is_authenticated and body:
            message = GroupMessage.objects.create(
                body=body,
                author=self.user,
                group=self.chatroom
            )
            print(f"[RECEIVE] Saved message {message.id} from user {self.user} in chatroom {self.chatroom_name}")

            event = {
                'type': 'chat_message',
                'message_id': message.id
            }
            async_to_sync(self.channel_layer.group_send)(
                self.chatroom_name,
                event
            )

    def chat_message(self, event):
        message = GroupMessage.objects.get(id=event['message_id'])
        print(f"[SEND] Sending message {message.id} to group {self.chatroom_name}")
        self.send(text_data=json.dumps({
            'type': 'chat.message',
            'message': {
                'id': message.id,
                'body': message.body,
                'author': message.author.username,
                'created_at': str(message.created_at),
                'group': message.group.group_name
            }
        }))

 