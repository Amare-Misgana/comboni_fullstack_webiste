from django.urls import re_path, path
from .consumers import ChatConsumer, OnlineStatus

websocket_urlpatterns = [
    re_path(r"ws/chat/(?P<roomname>[\w.@+-]+)/$",  ChatConsumer.as_asgi()),
    re_path(r"ws/online/", OnlineStatus.as_asgi()),
]