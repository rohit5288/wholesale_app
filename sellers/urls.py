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

    ## Events Management
    re_path(r'^my-events-list/$', MyEventsListAPI.as_view(), name='my_events_list'),
    re_path(r'^add-event/$',AddEventAPI.as_view(),name="add_event_api"),
    re_path(r'^update-event/$',UpdateEventAPI.as_view(),name="update_event_api"),
    re_path(r'^delete-event/$',DeleteEventAPI.as_view(),name="delete_event_api"),
    re_path(r'^change-event-status/$',ChangeEventStatusAPI.as_view(),name="change_event_status"),
    re_path(r'^boost-plans-list/$',EventBoostPlansListAPI.as_view(),name="boost-plans_list_api"),
    re_path(r'^boosted-events-list/$',BoostedEventsAPI.as_view(),name="boosted_events_list_api"),
    re_path(r'^boost-event/$',BoostEventAPI.as_view(),name="boost_event_api"),

    ##Ticket Management(Seller)
    re_path(r'^scan-ticket/$',ScanTicketAPI.as_view(),name="scan_ticket_api"),

    ##Promo Codes
    re_path(r'^promo-code-list/$',PromoCodesList.as_view(),name="promo_code_list"),
    re_path(r'^add-promo-code/$',AddPromoCode.as_view(),name="add_promo_code"),
    re_path(r'^update-promo-code/$',UpdatePromoCode.as_view(),name="update_promo_code"),
    re_path(r'^delete-promo-code/$',DeletePromoCode.as_view(),name="delete_promo_code"),
]
