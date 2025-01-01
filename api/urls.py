import os
import environ
from django.contrib import admin
from django.urls import re_path
from .views_authentication import *
env = environ.Env()
environ.Env.read_env()

admin.autodiscover()
app_name = 'api'


urlpatterns = [
    ## Authentication
    re_path(r'^user-signup-api/$',UserSignupView.as_view(),name="user_signup_api"),
    re_path(r'^user-login-api/$',UserLoginView.as_view(),name="user_login_api"),
    re_path(r'^check-user-api/$', UserCheckView.as_view(), name='check_user_api'),
    re_path(r'^delete-account-api/$',DeleteAccount.as_view(),name="delete_account_api"),
    re_path(r'^deactivate-account-api/$',DeactivateAccount.as_view(),name="deactivate_account_api"),
    re_path(r'^logout-api/$', LogoutView.as_view(), name='logout_api'),

    re_path(r'^verify-otp-api/$',VerifyOTP.as_view(),name="verify_otp_api"),
    re_path(r'^resend-otp-api/$',ResendOTP.as_view(),name="resend_otp_api"),

    re_path(r'^check-user-mail/$',CheckUserEmail.as_view(),name="check_user_mail"),
    
    re_path(r'^forgot-password-api/$',ForgotPassword.as_view(),name="forgot_password_api"),
    re_path(r'^forgot-password-resend-otp/$',ForgotPasswordResendOTP.as_view(),name="forgot_password_resend_otp_api"),
    
    ##Security Management
    re_path(r'^change-password-api/$',ChangePassword.as_view(),name="change_password_api"),
    re_path(r'^reset-password/$',ResetPasswordView.as_view(),name="reset_password_api"),

    ## Profile Management
    re_path(r'^profile-details-api/$',UserProfileDetails.as_view(),name="user_profile_details_api"),
    re_path(r'^update-profile-api/$',UpdateProfileDetails.as_view(),name="update_profile_api"),
    # re_path(r'^update-mobile-number-api/$',UpdateMobileNumberView.as_view(),name="update_mobile_number_api"),
    # re_path(r'^verify-mobile-number-api/$',VerifyMobileNumberView.as_view(),name="verify_mobile_number_api"),
    # re_path(r'^update-email-api/$',UpdatEmailAddressView.as_view(),name="update_email_api"),

    ## Static Pages
    re_path(r'^static-pages-api/$',StaticPages.as_view(),name="static_pages_api"),

    ## Faq Management
    re_path(r'^faq-list-api/$',FaqList.as_view(),name="faq_list_api"),
    
    ## Contact Us Management
    re_path(r'^contact-us-api/$',ContactUsView.as_view(),name="contact_us_api"),

    ## Notification Management
    re_path(r'^update-notification-settings-api/$',UpdateNotificationSettings.as_view(),name="update_notification_settings_api"),
    re_path(r'^notifications-list-api/$',NotificationsList.as_view(),name="notifications_list_api"),
    re_path(r'^clear-all-notifications-api/$',ClearAllNotifications.as_view(),name="clear_notifications_api"),
    re_path(r'^delete-notification-api/$',DeleteNotification.as_view(),name="delete_notification_api"),
    re_path(r'^mark-read-notification-api/$',MarkReadNotification.as_view(),name="mark_read_notification_api"),
    
]