from django.db.models import Q
from accounts.constants import *
from .models import *
from rest_framework.serializers import ModelSerializer, SerializerMethodField, CharField
from .models import *


class UserChatsListSerializer(ModelSerializer):
    receiver = SerializerMethodField(read_only = True)
    last_message = SerializerMethodField(read_only = True)
    unread_messages = SerializerMethodField(read_only = True)

    class Meta:
        model = Chatting
        fields = ('id','last_message','receiver','unread_messages')


    def get_unread_messages(self,obj):
        request = self.context.get('request')
        return Message.objects.filter(chat=obj,seen=False, receiver=request.user).exclude(deleted_by=request.user).count()
    

    def get_receiver(self, obj):
        request = self.context.get('request')
        if obj.sender.id == request.user.id:
            receiver = obj.receiver
        else:
            receiver = obj.sender
        return {
            "id":receiver.id,
            "full_name":receiver.full_name if receiver.full_name else "",
            "profile_pic":request.build_absolute_uri(receiver.profile_pic.url) if receiver.profile_pic else "",
        } if obj.receiver else {}
    
    def get_last_message(self, obj):
        request = self.context.get('request')
        message = Message.objects.filter(chat=obj).exclude(deleted_by=request.user).order_by('-created_on').first()
        return {
            "sender":message.sender.id,
            "message":message.message,
            "message_file":self.context.get('request').build_absolute_uri(message.message_file.url) if message.message_file else "",
            "created_on":message.created_on.strftime("%Y-%m-%d %H:%M:%S")
        } if message else {}
    
    

class MessageSerializer(ModelSerializer):
    created_on = SerializerMethodField(read_only = True)
    sender = SerializerMethodField(read_only = True)
    class Meta:
        model = Message
        fields = ('id','sender','receiver','message','message_file','created_on')

    def get_created_on(self, obj):
        return obj.created_on.strftime("%Y-%m-%d %H:%M:%S")
    
    def get_sender(self, obj):
        return {
            "id":obj.sender.id,
            "full_name":obj.sender.full_name,
            "profile_pic":self.context.get('request').build_absolute_uri(obj.sender.profile_pic.url) if obj.sender.profile_pic else "",
        } if obj.sender else {}
    

class WebMessageSerializer(ModelSerializer):
    class Meta:
        model = Message
        fields = ('id','message','created_on','sender')