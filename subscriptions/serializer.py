from rest_framework.serializers import ModelSerializer, SerializerMethodField, CharField
from subscriptions.models import *
from datetime import datetime 


class SubscriptionSerializer(ModelSerializer):
    class Meta:
        model = SubscriptionPlans
        fields = ('__all__')

