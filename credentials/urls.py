from .views import *
from django.contrib import admin
from django.urls import re_path
admin.autodiscover()
app_name = 'credentials'

urlpatterns = [
    ## SMTP Settings
    re_path(r'^smtp-list/$',SMTPListView.as_view(),name="smtp_list"),
    re_path(r'^add-smtp/$',AddSMTPView.as_view(),name="add_smtp"),
    re_path(r'^delete-smtp/(?P<id>[-\w]+)/$', DeleteSMTP.as_view(), name='delete_smtp'),
    re_path(r'^view-smtp/(?P<id>[-\w]+)/$', ViewSMTP.as_view(), name='view_smtp'),
    re_path(r'^edit-smtp/(?P<id>[-\w]+)/$', EditSMTP.as_view(), name='edit_smtp'),
    re_path(r'^active-deactive-smtp/(?P<id>[-\w]+)/$', ActivateDeActiveSMTP.as_view(), name='active_deactive_smtp'),

    ##Firebase Credentials
    re_path(r'^firebase-credentials-list/$',FirebaseCredentialsList.as_view(),name="firebase_credentials_list"),
    re_path(r'^add-firebase-credentials/$',AddFirebaseCredentials.as_view(),name="add_firebase_credentials"),
    re_path(r'^view-firebase-credentials/(?P<id>[-\w]+)/$',ViewFirebaseCredentials.as_view(),name="view_firebase_credentials"),
    re_path(r'^change-firebase-status/(?P<id>[-\w]+)/$',ActivateFirebaseStatus.as_view(),name="change_firebase_status"),
    re_path(r'^update-firebase-credentials/(?P<id>[-\w]+)/$',UpdateFirebaseCredential.as_view(),name="update_firebase_credentials"),
    re_path(r'^delete-firebase-credentials/(?P<id>[-\w]+)/$',DeleteFirebase.as_view(),name="delete_firebase_credentials"),

    ## Stripe Settings
    re_path(r'^stripe-list/$',StripeListView.as_view(),name="stripe_list"),
    re_path(r'^add-stripe/$',AddStripeKeyView.as_view(),name="add_stripe"),
    re_path(r'^delete-stripe/(?P<id>[-\w]+)/$', DeleteStripeKey.as_view(), name='delete_stripe'),
    re_path(r'^view-stripe/(?P<id>[-\w]+)/$', ViewStripeKey.as_view(), name='view_stripe'),
    re_path(r'^edit-stripe/(?P<id>[-\w]+)/$', EditStripeKey.as_view(), name='edit_stripe'),
    re_path(r'^active-deactive-stripe/(?P<id>[-\w]+)/$', ActivateDeActiveStripeKey.as_view(), name='active_deactive_stripe'),
]