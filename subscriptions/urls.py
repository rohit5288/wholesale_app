from django.contrib import admin
from .views import *
from .views_api import *
from django.urls import re_path,path


admin.autodiscover()
app_name = 'subscriptions'


urlpatterns = [

    ## Subscription Plans
    re_path(r'^subscription-plans-list/$', AllSubscriptionPlans.as_view(), name='all_plans'),
    re_path(r'^add-subscription-plan/$', AddSubscriptionPlan.as_view(), name='add_subscription_plan'),
    re_path(r'^view-subscription-plan/(?P<id>[-\w]+)/',ViewSubscriptionPlan.as_view(),name="view_plan"),
    re_path(r'^edit-plan/(?P<id>[-\w]+)/$',EditSubscriptionPlan.as_view(), name='edit_plan'),
    re_path(r'^delete-plan/(?P<id>[-\w]+)/$',DeleteSubscriptionPlan.as_view(), name='delete_plan'),
    re_path(r'^add-default-subscription/$',AddDefaultSubscription.as_view(), name='add_default_plan'),

    ## Event Booster Plans
    re_path(r'^booster-plans-list/$', AllEventBoosterPlans.as_view(), name='all_booster_plans'),
    re_path(r'^add-booster-plan/$', AddEventBoosterPlan.as_view(), name='add_booster_plan'),
    re_path(r'^view-booster-plan/(?P<id>[-\w]+)/',ViewEventBoosterPlan.as_view(),name="view_booster_plan"),
    re_path(r'^edit-booster-plan/(?P<id>[-\w]+)/$',EditEventBoosterPlan.as_view(), name='edit_booster_plan'),
    re_path(r'^delete-booster-plan/(?P<id>[-\w]+)/$',DeleteEventBoosterPlan.as_view(), name='delete_booster_plan'),
    re_path(r'^add-default-booster-subscription/$',AddDefaultBoosterPlans.as_view(), name='add_default_booster_plan'),

    #SubScriptions
    re_path(r'^subscription-listing/$',SubscriptionListing.as_view(),name="subscription_listing"),
    re_path(r'^subscription-plan-purchase/$',SubscriptionPurchase.as_view(),name="subscription_plan_purchase"),
]