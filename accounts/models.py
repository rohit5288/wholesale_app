import uuid
from .constants import *
from django.db import models
from django.contrib.auth.models import AbstractUser
import environ

env = environ.Env()
environ.Env.read_env()

class CommonInfo(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_on = models.DateTimeField(auto_now_add=True,null=True,blank=True)
    updated_on = models.DateTimeField(auto_now=True,null=True,blank=True)

    class Meta:
        abstract = True


class User(AbstractUser,CommonInfo):
    username = models.CharField(max_length=255,blank=True, null=True, unique=True)
    full_name = models.CharField(max_length=255,null=True,blank=True)
    first_name = models.CharField(max_length=255,null=True,blank=True)
    last_name = models.CharField(max_length=255,null=True,blank=True)
    mobile_no = models.CharField(max_length=20, null=True, blank=True)
    country_iso_code = models.CharField(max_length=10, null=True, blank=True)
    country_code = models.CharField(max_length=20, null=True, blank=True)
    customer_id = models.CharField(max_length=255,null=True,blank=True)
    profile_pic = models.FileField(upload_to='profile_pic/', blank=True, null=True)
    role_id = models.PositiveIntegerField(default=ADMIN,choices=USER_ROLE,null=True, blank=True)
    dob = models.DateField(null=True, blank=True)
    status = models.PositiveIntegerField(default=ACTIVE, choices=USER_STATUS,null=True, blank=True)
    temp_otp = models.CharField(max_length=4, null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    is_profile_setup = models.BooleanField(default=False)
    notification_enable = models.BooleanField(default=True)
    event_notification =  models.BooleanField(default=True)
    blog_notification =  models.BooleanField(default=True)
    email_notification = models.BooleanField(default=False)
    sms_notification = models.BooleanField(default=False)
    social_id = models.CharField(max_length=255, null=True, blank=True)
    social_type = models.PositiveIntegerField(default=6,choices=SOCIAL_TYPE, null=True, blank=True)
    gender = models.PositiveIntegerField(choices=GENDER, null=True, blank=True)
    is_plan_purchased = models.BooleanField(default=False)
    about = models.TextField(null=True,blank=True)
    #Address
    address=models.TextField(null=True,blank=True)
    latitude=models.FloatField(null=True,blank=True)
    longitude=models.FloatField(null=True,blank=True)

    class Meta:
        managed = True
        default_permissions = ()
        db_table = 'user'

    def __str__(self):
        return str(self.first_name)


class Images(CommonInfo):
    file = models.FileField(upload_to='images/',blank=True,null=True)

    class Meta:
        managed = True
        db_table = 'images'


class Device(CommonInfo):
    user = models.ForeignKey('User',null=True,blank=True,on_delete=models.CASCADE)
    device_type = models.PositiveIntegerField(choices=DEVICE_TYPE,null=True,blank=True)
    device_name = models.CharField(max_length=255,null=True,blank=True)
    device_token = models.TextField(null=True,blank=True)
    
    class Meta:
        managed = True
        default_permissions = ()
        db_table = 'device'


class LoginHistory(CommonInfo):
    user_ip = models.CharField(max_length=255, null=True, blank=True)
    user_ip = models.CharField(max_length=255, null=True, blank=True)
    user_agent = models.CharField(max_length=255, null=True, blank=True)
    status = models.PositiveIntegerField(null=True, blank=True, choices=LOGIN_STATE)
    url = models.CharField(max_length=255, null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True,null=True, blank=True)
    user_email = models.CharField( max_length=255, null=True, blank=True)
    mobile_no = models.CharField(max_length=20, null=True, blank=True)
    country_code = models.CharField(max_length=20, null=True, blank=True)

    class Meta:
        managed = True
        db_table = 'login_history'
        default_permissions = ()


class Notifications(CommonInfo):
    title = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    is_read = models.BooleanField(default=False)
    notification_type = models.PositiveIntegerField(null=True, blank=True, choices=NOTIFICATION_TYPE)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications", null=True, blank=True)
    created_for = models.ForeignKey(User, on_delete=models.CASCADE, related_name="_notifications", null=True, blank=True)
    obj_id =models.CharField(max_length=255,null=True,blank=True)

    class Meta:
        managed = True
        db_table = 'notifications'
        default_permissions = ()


class TempOtpValidation(CommonInfo):
    mobile_no = models.CharField(max_length=20, null=True, blank=True, unique=True)
    country_code = models.CharField(max_length=20, null=True, blank=True)
    country_iso_code = models.CharField(max_length=20, null=True, blank=True)
    temp_otp = models.CharField(max_length=4, null=True, blank=True)

    class Meta:
        managed = True
        default_permissions = ()
        db_table = 'tbl_temp_otp_validation'


class Banners(CommonInfo):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255,blank=True,null=True)
    image = models.ImageField(upload_to='banner',blank=True,null=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True)

    class Meta:
        managed = True
        default_permissions = ()
        db_table = 'tbl_banners'


class ProjectLogo(CommonInfo):
    logo = models.FileField(upload_to='lg_logo',null=True, blank=True)
    favicon = models.FileField(upload_to='favicon_logo',null=True, blank=True)
    created_by = models.ForeignKey(User,on_delete=models.CASCADE,max_length=True,blank=True)

    class Meta:
        managed = True
        default_permissions = ()
        db_table = 'tbl_project_logo'


class AdminServiceFees(CommonInfo):
    service_fees = models.FloatField(max_length=50,null=True,blank=True)

    class Meta:
        managed = True
        default_permissions = ()
        db_table = 'tbl_platform_service_fees'

class Activities(CommonInfo):
    title = models.CharField(max_length=255,null=True,blank=True)
    description = models.TextField(null=True,blank=True)
    user = models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True)
    activity_type = models.PositiveIntegerField(null=True, blank=True, choices=USER_ACTIVITY_TYPE)
    object_id = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        managed = True
        db_table = 'tbl_user_activity'  
        default_permissions = ()