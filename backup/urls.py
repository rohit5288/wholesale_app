from .views import *
from django.urls import re_path
from django.contrib import admin


admin.autodiscover()
app_name = 'backup'


urlpatterns = [
    re_path(r'^$', BackupsList.as_view(), name='backup'),
    re_path(r'^database-backup/$', CreateDBBackup.as_view(), name='database_backup'),
    re_path(r'^database-schema/$', CreateDBSchema.as_view(), name='database_schema'),
    re_path(r'^delete-backup/(?P<id>[-\w]+)/$', DeleteBackup.as_view(), name='delete_backup'),
]