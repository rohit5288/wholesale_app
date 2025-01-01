from rest_framework.serializers import ModelSerializer, SerializerMethodField, CharField
from .models import *


class ApplicationCrashLogsSerializer(ModelSerializer):
    class Meta:
        model=ApplicationCrashLogs
        fields="__all__"