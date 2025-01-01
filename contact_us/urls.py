from django.contrib import admin
from .views import *
from django.urls import re_path


admin.autodiscover()
app_name = 'contact_us'


urlpatterns = [

    ## Contact Us
    re_path(r'contact-us-list/$',ContactUsList.as_view(),name="contactus_list"),
    re_path(r'view-contact-us-details/(?P<id>[-\w]+)/$',ViewContactUsDetails.as_view(),name="view_contact"),
    re_path(r'delete-contact-us/(?P<id>[-\w]+)/$',DeleteContactUs.as_view(),name="delete_contact"),
    re_path(r'contactus-reply/$',ContactUsReplyView.as_view(),name="contactus_reply"),
    re_path(r'contact-us-view/$',ContactUsView.as_view(),name="contact_us_view"),
    re_path(r'clear-admin-details/$',ClearAdminDetails.as_view(),name="clear_admin_details"),
    
    ## Contact Details
    re_path(r'update-contact-details/$',UpdateContactDetails.as_view(),name="update_contact_details"),
    re_path(r'update-social-links/$',UpdateSocialLinks.as_view(),name="social_links"),
    re_path(r'clear-social-links/$',ClearSocialLinks.as_view(),name="clear_social_links"),

]
