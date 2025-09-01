"""
ASGI config for django_backend project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from . import routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_backend.settings')

application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': URLRouter(routing.websocket_urlpatterns),
})


# import os 
# from django.core.asgi import get_asgi_appli ation
# from channels.routing import ProtocolTypeRouter,URLRouter
# #导入chat应用中的路由模块
# from . import routings
 
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_backend.settings')
# application = ProtocolTypeRouter({
#     #http路由走这里
#     "http":get_asgi_application(),
#     #chat应用下rountings模块下的路由变量socket_urlpatterns
#     "websocket":URLRouter(routings.socket_urlpatterns)
# })