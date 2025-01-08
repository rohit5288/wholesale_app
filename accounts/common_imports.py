import os
import json
import environ
import logging
import pandas as pd
from accounts .utils import *
from django.db.models import Q,F,Count,Sum,Min,Max
from datetime import datetime, date, timedelta
from django.urls import reverse
from django.template.loader import render_to_string
from django.conf import settings
from django.views.generic import TemplateView,View
from accounts.constants import *
from django.utils.decorators import method_decorator
from accounts.decorators import *
from django.shortcuts import render , redirect, HttpResponseRedirect
from django.http import JsonResponse
from django.contrib import messages
from django.db.models import Exists,OuterRef
from django.db.models.functions import Radians, Power, Sin, Cos, ATan2, Sqrt, Radians

## API's
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token 
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer, SerializerMethodField, CharField, Serializer
from rest_framework import status,permissions
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.parsers import MultiPartParser,FormParser
import stripe

env = environ.Env()
environ.Env.read_env()


## Required Fields Validator
from api.helper import RequiredFieldValidations