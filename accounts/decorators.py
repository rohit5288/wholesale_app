from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from accounts.constants import *
from functools import wraps
from django.shortcuts import render,redirect


def admin_only(function):
    @login_required
    @wraps(function)
    def wrap(request, *args, **kwargs):
        if request.user.is_superuser:
            return function(request, *args, **kwargs)
        else:
            return render(request, 'frontend/404.html')
    return wrap