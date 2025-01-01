from django.contrib import admin
from .views import *
from django.urls import re_path


admin.autodiscover()
app_name = 'static_pages'


urlpatterns = [

    ## Pages
    re_path(r'^pages-list/$',PagesListView.as_view(),name="pages_list"),
    re_path(r'^add-page/$',AddPageView.as_view(),name="add_page"),
    re_path(r'^delete-page/(?P<id>[-\w]+)/$', DeletePage.as_view(), name='delete_page'),
    re_path(r'^view-page/(?P<id>[-\w]+)/$', ViewPage.as_view(), name='view_page'),
    re_path(r'^edit-page/(?P<id>[-\w]+)/$', EditPage.as_view(), name='edit_page'),
    re_path(r'^change-page-status/(?P<id>[-\w]+)/$',ChangePageStatus.as_view(), name='change_page_status'),


    ## FAQs
    re_path(r'^faqs-list/$',FaqsList.as_view(),name="faq_list"),
    re_path(r'^add-faq/$',AddFAQ.as_view(),name="add_faq"),
    re_path(r'^delete-faq/(?P<id>[-\w]+)/$', DeleteFAQ.as_view(), name='delete_faq'),
    re_path(r'^delete-all-fAQ/$', DeleteAllFAQ.as_view(), name='delete_all_fAQ'),
    re_path(r'^view-faq/(?P<id>[-\w]+)/$', ViewFAQ.as_view(), name='view_faq'),
    re_path(r'^edit-faq/(?P<id>[-\w]+)/$', UpdateFAQ.as_view(), name='edit_faq'),
    
]
