import os
import environ
from django.contrib import admin
from django.urls import re_path
from .views_api import *
from .views_api import *
from .views import *
env = environ.Env()
environ.Env.read_env()

admin.autodiscover()
app_name = 'sellers'

urlpatterns = [
    # Seller Management Admin Panel
    re_path(r'^seller-list/$', SellerList.as_view(), name='seller_list'),
    re_path(r'^seller-graph/$', SellersGraph.as_view(), name='seller_graph'),
]
