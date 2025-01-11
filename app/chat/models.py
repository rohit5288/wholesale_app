from django.db import models
from accounts.models import *
# Create your models here.


class Chatting(CommonInfo):
    sender = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE, related_name='sender')
    receiver = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE, related_name='receiver')

    class Meta:
        managed = True
        default_permissions = ();
        db_table = 'chatting'


class Message(CommonInfo):
    sender = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE, related_name='sender_message')
    receiver = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE, related_name='receiver_message')
    message = models.TextField(null=True,blank=True)
    message_file = models.FileField(upload_to='message_files/', null=True, blank=True)
    chat = models.ForeignKey(Chatting,on_delete=models.CASCADE, null=True, blank=True)
    seen = models.BooleanField(default=False)
    deleted_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE, related_name='deleted_by')

    class Meta:
        managed = True;
        db_table = 'messages'
        default_permissions = ()