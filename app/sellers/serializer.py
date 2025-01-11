from rest_framework.serializers import ModelSerializer, SerializerMethodField, CharField
from .models import *
from api.serializer import *
from datetime import datetime,timedelta



class PromoCodesSerializer(ModelSerializer):
    class Meta:
        model = PromoCodes
        fields = "__all__"

