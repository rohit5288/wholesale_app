import os
import environ
from django.contrib import admin
from django.urls import re_path
from .views import *
from .views_api import *
env = environ.Env()
environ.Env.read_env()

admin.autodiscover()
app_name = 'blog'
urlpatterns = [
    ## Blog Management
    re_path(r'^blog-list/$', BlogList.as_view(), name='blog_list'),
    re_path(r'^add-blog/$', AddBlog.as_view(), name='add_blog'),
    re_path(r'^update-blog/(?P<id>[-\w]+)/$', UpdateBlog.as_view(), name='update_blog'),
    re_path(r'^view-blog/(?P<id>[-\w]+)/$', ViewBlogDetails.as_view(), name='view_blog'),
    re_path(r'^delete-blog/(?P<id>[-\w]+)/$', DeleteBlog.as_view(), name='delete_blog'),
    re_path(r'^change-blog-status/(?P<id>[-\w]+)/$', ChangeBlogStatus.as_view(), name='change_blog_status'),

    ## Blog APIs
    re_path(r'^blog-list-api/$', BlogsListAPI.as_view(), name='blogs_api'),
    re_path(r'^blog-details-api/$', ViewBlogAPI.as_view(), name='blog_details_api'),
    
]
