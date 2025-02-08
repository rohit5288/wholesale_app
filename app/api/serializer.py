from static_pages.models import *
from rest_framework.serializers import ModelSerializer, SerializerMethodField, CharField
from rest_framework.authtoken.models import Token 
from contact_us.models import *
from django.db.models import Q
from api.helper import *

class AddressSerializer(ModelSerializer):
    class Meta:
        model=Address
        fields="__all__"


class UserSerializer(ModelSerializer):
    token = SerializerMethodField(read_only=True)
    profile_pic =SerializerMethodField()
    
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
        fields= ("id","first_name","last_name","full_name","role_id","address","last_login","profile_pic","email","temp",
                 "mobile_no","country_code","country_iso_code","status","temp_otp","is_profile_setup",
                 "notification_enable","token","created_on","updated_on",)


class SellerSerializer(ModelSerializer):
    token = SerializerMethodField(read_only=True)
    profile_pic=SerializerMethodField()
    address=AddressSerializer()
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
        fields= ("id","first_name","last_name","full_name","business_name","role_id","address","last_login","profile_pic","email","temp",
                 "mobile_no","country_code","country_iso_code","status","temp_otp","is_profile_setup","gst_no","gst_document",
                 "notification_enable","token","created_on","updated_on")


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
