import os
import django
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_heart.settings')
django.setup()

from apis.api_heart_tv.routing import websocket_urlpatterns
application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    ),
})

# application = ProtocolTypeRouter({
#     "http": get_asgi_application(),
#     "websocket": TenantWebSocketMiddleware(
#         AuthMiddlewareStack(
#             URLRouter(
#                 websocket_urlpatterns
#             )
#         )
#     ),
# })
