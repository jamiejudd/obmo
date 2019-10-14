from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
import json

from core.models import Account, Arrow, Challenge, ChallengeLink, Message, MessageCh

from django.utils import timezone

class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.user = self.scope["user"]
        #print(self.user.username)
        #print(self.channel_name)

        self.room_name = self.scope['url_route']['kwargs']['room_name']
        #print(self.room_name)
        self.room_group_name = 'chat_%s' % self.room_name
        #print(self.room_group_name)

        account = Account.objects.filter(public_key = self.user.username).first()

        if account is not None and account.suspended == False and self.user.username == self.room_name:
            # Join room group
            async_to_sync(self.channel_layer.group_add)(
                self.room_group_name,
                self.channel_name
            )
            self.accept()
        else:
            self.send({"close": True})


    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        sender = self.scope["user"].username
        target = text_data_json['target']
        target_type = text_data_json['target_type']

        if target_type == 'account':
            sender_account = Account.objects.filter(public_key = sender).first()
            target_account = Account.objects.filter(public_key = target).first()
            if sender_account is not None and target_account is not None:
                arrow = Arrow.objects.filter(source=sender_account,target=target_account).first()
                if arrow is not None:
                    Message.objects.create(sender=sender_account,recipient=target_account,content=message,timestamp=timezone.now())
                    arrow.has_new_message = True
                    arrow.save()
                    target_group_name = 'chat_%s' % target

                    # Send message to room group
                    async_to_sync(self.channel_layer.group_send)(
                        target_group_name,
                        {
                            'type': 'chat_message_in',
                            'message': message,
                            'target': sender,
                            'sender_name': '', 
                            'sender_public_key': '' 
                        }
                    )
                    # Send message to room group
                    async_to_sync(self.channel_layer.group_send)(
                        self.room_group_name,
                        {
                            'type': 'chat_message_out',
                            'message': message,
                            'target': target
                        }
                    )
        else:
            sender_account = Account.objects.filter(public_key = sender).first()
            target_challenge = Challenge.objects.filter(id = target).first()
            if sender_account is not None and target_challenge is not None:
                challengelink = ChallengeLink.objects.filter(voter=sender_account,challenge=target_challenge).first()
                if challengelink is not None:
                    MessageCh.objects.create(sender=sender_account,challenge=target_challenge,content=message,timestamp=timezone.now())
                    other_challengelinks = ChallengeLink.objects.filter(challenge=target_challenge).exclude(voter=sender_account)
                    for cl in other_challengelinks:
                        cl.has_new_message = True
                        cl.save()   
                        target_group_name = 'chat_%s' % cl.voter.public_key   
                        # Send message to room group
                        async_to_sync(self.channel_layer.group_send)(
                            target_group_name,
                            {
                                'type': 'chat_message_in',
                                'message': message,
                                'target': target,
                                'sender_name': sender_account.name,
                                'sender_public_key': sender_account.public_key
                            }
                        )

                    # Send message to room group
                    async_to_sync(self.channel_layer.group_send)(
                        self.room_group_name,
                        {
                            'type': 'chat_message_out',
                            'message': message,
                            'target': target
                        }
                    )


    # Receive message from room group
    def chat_message_out(self, event):
        message = event['message']
        target = event['target']

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'event_type': 'message_out',
            'message': message,
            'target': target
        }))

    # Receive message from room group
    def chat_message_in(self, event):
        message = event['message']
        target = event['target']
        sender_name = event['sender_name']
        sender_public_key = event['sender_public_key']

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'event_type': 'message_in',
            'message': message,
            'target': target,
            'sender_name': sender_name,
            'sender_public_key': sender_public_key
        }))

    # # Receive message from room group
    # def mark_read(self, event):
    #     target = event['target']

    #     # Send message to WebSocket
    #     self.send(text_data=json.dumps({
    #         'event_type': 'mark_read',
    #         'target': target
    #     }))