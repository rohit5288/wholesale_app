from django.db.models import Q
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from accounts.constants import *


User = get_user_model()

class EmailLoginBackend(ModelBackend):

    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = User.objects.filter(Q(username=username)|Q(email=username)).last()
        except User.DoesNotExist:
            return None
        if user.check_password(password):
            return user


