from django.db import models
from accounts.models import *

class SMTPSetting(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email_backend = models.TextField(null=True, blank=True)
    email_host = models.TextField(null=True, blank=True)
    email_port = models.CharField(max_length=255, blank=True, null=True)
    use_tls = models.BooleanField(default=True, blank=True, null=True)
    email_host_user = models.CharField(max_length=255, blank=True, null=True)
    email_host_password = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=False, blank=True, null=True)
    created_on = models.DateTimeField(auto_now_add=True,null=True, blank=True)
    updated_on = models.DateTimeField(auto_now=True,null=True, blank=True)

    class Meta:
        default_permissions = ()
        db_table = 'tbl_smtp_settings'


class FirebaseCredentials(CommonInfo):
    key = models.TextField(null=True, blank=True)
    active = models.BooleanField(default=False)

    class Meta:
        managed = True
        default_permissions = ()
        db_table = 'firebase_credentials'

class StripeSetting(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    test_secretkey = models.TextField(null=True, blank=True)
    test_publishkey = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=False, blank=True, null=True)
    created_on = models.DateTimeField(auto_now_add = True,null=True, blank=True)
    created_by = models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True)

    class Meta:
        default_permissions = ()
        db_table = 'stripe_settings'
