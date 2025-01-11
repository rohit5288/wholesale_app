import uuid
from django.db import models
from accounts.models import *


class ContactUs(CommonInfo):
    full_name = models.CharField(max_length=255, null=True, blank=True)
    subject = models.CharField(max_length=255,null=True,blank=True)
    email = models.CharField(max_length=255, null=True, blank=True)
    message = models.TextField(null=True, blank=True)

    class Meta:
        managed = True
        default_permissions = ();
        db_table = 'tbl_contactus'


class ContactUsReply(CommonInfo):
    contact = models.ForeignKey('ContactUs',null=True,blank=True,on_delete=models.CASCADE)
    reply_message = models.TextField(null=True, blank=True)
    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE, related_name="replied_to")

    class Meta:
        managed = True
        default_permissions = ();
        db_table = 'tbl_contactus_reply'



class ContactDetails(CommonInfo):
    email = models.EmailField(null=True, blank=True, max_length=255)
    country_code = models.CharField(max_length=10, null=True, blank=True)
    country_iso_code = models.CharField(max_length=10, null=True, blank=True)
    mobile_no = models.CharField(max_length=20, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    facebook_url = models.CharField(max_length=250,null=True, blank=True)
    twitter_url = models.CharField(max_length=250,null=True, blank=True)
    google_url = models.CharField(max_length=250,null=True, blank=True)

    class Meta:
        managed = True
        default_permissions = ();
        db_table = 'tbl_contact_details'