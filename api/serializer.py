from static_pages.models import *
from rest_framework.serializers import ModelSerializer, SerializerMethodField, CharField
from rest_framework.authtoken.models import Token 
from contact_us.models import *
from django.db.models import Q
from api.helper import *
from events.models import *


class UserSerializer(ModelSerializer):
    token = SerializerMethodField(read_only=True)
    profile_pic =SerializerMethodField()
    is_followed=SerializerMethodField()
    followers_count=SerializerMethodField()
    
    def get_is_followed(self,obj):
        request=self.context.get('request')
        return IsFollowed(request,obj)
    
    def get_followers_count(self,obj):
        request=self.context.get('request')
        return GetFollowersCount(request,obj)
    
    def get_profile_pic(self,obj):
        url=self.context.get('request').build_absolute_uri(obj.profile_pic.url) if obj.profile_pic else "" 
        if url:
            url=url.split('://')[1]
            return  'https://'+url if USE_HTTPS else 'http://' + url 
        return None
    
    def get_token(self, obj):
        request = self.context.get('request')
        try:
            token = Token.objects.get(user=obj)
        except:
            token = Token.objects.create(user=obj)
        return token.key

    class Meta:
        model=User
        fields= ("id","first_name","last_name","full_name","gender","dob","role_id","address","latitude","longitude","last_login","profile_pic","email",
                 "mobile_no","country_code","country_iso_code","status","temp_otp","is_verified","is_profile_setup",
                 "notification_enable","token","created_on","updated_on","is_followed","followers_count",
                "tiktok_link","facebook_link","instagram_link","twitter_link","linkedin_link")


class SellerSerializer(ModelSerializer):
    token = SerializerMethodField(read_only=True)
    profile_pic=SerializerMethodField()
    is_followed=SerializerMethodField()
    followers_count=SerializerMethodField()
    posted_events_count=SerializerMethodField()

    def get_posted_events_count(self,obj):
        request=self.context.get('request')
        return Events.objects.filter(created_by=obj,status=ACTIVE).count()
    
    def get_is_followed(self,obj):
        request=self.context.get('request')
        return IsFollowed(request,obj)
    
    def get_followers_count(self,obj):
        request=self.context.get('request')
        return GetFollowersCount(request,obj)
    
    def get_profile_pic(self,obj):
        url=self.context.get('request').build_absolute_uri(obj.profile_pic.url) if obj.profile_pic else "" 
        if url:
            url=url.split('://')[1]
            return  'https://'+url if USE_HTTPS else 'http://' + url 
        return None
    
    def get_token(self, obj):
        request = self.context.get('request')
        try:
            token = Token.objects.get(user=obj)
        except:
            token = Token.objects.create(user=obj)
        return token.key
    class Meta:
        model=User
        fields= ("id","first_name","last_name","full_name","gender","dob","role_id","address","latitude","longitude","last_login","profile_pic","email",
                 "mobile_no","country_code","country_iso_code","status","temp_otp","is_verified","is_profile_setup",
                 "notification_enable","token","created_on","updated_on","is_followed","followers_count","posted_events_count",
                "tiktok_link","facebook_link","instagram_link","twitter_link","linkedin_link")


class MinorUserSerializer(ModelSerializer):
    profile_pic=SerializerMethodField()
    def get_profile_pic(self,obj):
        url=self.context.get('request').build_absolute_uri(obj.profile_pic.url) if obj.profile_pic else "" 
        if url:
            url=url.split('://')[1]
            return  'https://'+url if USE_HTTPS else 'http://' + url 
        return None
    class Meta:
        model=User
        fields= ("id","full_name","profile_pic")


class PagesSerializer(ModelSerializer):
    class Meta:
        model = Pages
        fields = ('type_id','title','content')

class FaqSeializer(ModelSerializer):
    class Meta:
        model = FAQs
        fields = fields = ('id','question','answer','created_on')

  
class ContactUsSerializer(ModelSerializer):
    class Meta:
        model = ContactUs
        fields = ('id','full_name','subject','email','message','created_on')



class UserProfileSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class NotificationSerializer(ModelSerializer):
    class Meta:
        model = Notifications
        fields = '__all__'
