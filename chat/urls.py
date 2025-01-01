from .views_api import *
from django.urls import re_path
from django.contrib import admin

admin.autodiscover()
app_name = 'chat'

urlpatterns = [
    ## Chat API's 
    re_path(r'^chats-list/$',UserChatsList.as_view(),name="user_chats_list"),
    re_path(r'^send-message/$',SendMessage.as_view(),name="send_message"),
    re_path(r'^message-window/$',MessageWindowAPI.as_view(),name="message_window"),
    re_path(r'^load-messages/$',LoadMessageAPI.as_view(),name="load_messages"),
    # re_path(r'^delete-chat/$',DeleteChatHistory.as_view(),name="delete_chat"),
    # re_path(r'^mute-unmute-chat/$',MuteUnmuteChat.as_view(),name="mute_unmute_chat"),
    # re_path(r'^pin-unpin-message/$',PinUnpinMessage.as_view(),name="pin_unpin_message"),
]