from django.urls import re_path
from channels.routing import ProtocolTypeRouter, URLRouter
from registro.consumers import CameraConsumer  # Confirme o caminho correto do seu consumer

websocket_urlpatterns = [
    re_path(r'ws/camera/$', CameraConsumer.as_asgi()),
]
