from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'websocket/$', consumers.MyConsumer.as_asgi()),
]