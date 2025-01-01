from .views import *
from django.contrib import admin
from django.urls import re_path
from .views_graphs import *
from .views_exports import *
admin.autodiscover()
app_name = 'users'


urlpatterns = [

    ## Users
    re_path(r'^view-profile/(?P<id>[-\w]+)/$',ViewUser.as_view(), name='view_user'),
    re_path(r'^edit-admin/(?P<id>[-\w]+)/$',EditAdmin.as_view(), name='edit_admin'),
    re_path(r'^customers-list/$', BuyersList.as_view(), name='customers_list'),
    re_path(r'^add-user/$', AddUser.as_view(), name='add_user'),
    re_path(r'^edit-user/(?P<id>[-\w]+)/$', EditUser.as_view(), name='edit_user'),

    ## User Actions
    re_path(r'^deactivate-user/(?P<id>[-\w]+)/$',InactivateUser.as_view(), name='inactivate_user'),
    re_path(r'^delete-user/(?P<id>[-\w]+)/$',DeleteUser.as_view(), name='delete_user'),
    re_path(r'^activate-user/(?P<id>[-\w]+)/$',ActivateUser.as_view(), name='activate_user'),

    ## Panel Graphs
    re_path(r'^user-graph/$', UserGraph.as_view(), name='users_graph'),
    # re_path(r'^revenue-graph/$',RevenueGraph.as_view(), name='revenue_graph'),
    re_path(r'^users-analytical-graph/$',UserAnalyticGraphdata.as_view(), name='users_analytical_graph'),

    ## Download
    re_path(r'^download-customer-reports/$',DownLoadBuyerReports.as_view(), name='download_customer_reports'),

    re_path(r'^revenue-graph-weekly/$', RevenueGraphWeekly.as_view(), name='revenue_graph_weekly'),
    re_path(r'^revenue-graph/$', RevenueGraph.as_view(), name='revenue_graph'),
    re_path(r'^booking-graph/$', TicketBookingGraph.as_view(), name='booking_graph'),
]