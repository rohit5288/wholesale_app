from blog.models import *
from accounts.models import *
from rest_framework.serializers import ModelSerializer, SerializerMethodField, CharField
from rest_framework.authtoken.models import Token 
from django.db.models import Q


class BlogSerializer(ModelSerializer):
    images=SerializerMethodField()
    def get_images(self,obj):
        request=self.context.get('request')
        return [request.build_absolute_uri(img.image.url) for img in obj.images.all()]

    class Meta:
        model=Blogs
        fields="__all__"