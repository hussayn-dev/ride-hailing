from django.urls import re_path

from location.consumers import TripLocationConsumer

websocket_patterns = [
    re_path(r"^ws/trip-location/$", TripLocationConsumer.as_asgi()),
]
