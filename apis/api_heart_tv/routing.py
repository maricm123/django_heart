from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/coach_preview/$', consumers.CoachPreviewConsumer.as_asgi()),
    re_path(r'ws/gym/$', consumers.GymConsumer.as_asgi()),  # novo za TV
    # re_path(r'ws/bpm/(?P<tenant_id>\d+)/$', consumers.BPMConsumer.as_asgi()),
]
