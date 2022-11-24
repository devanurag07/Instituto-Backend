from django.urls import path

from . import consumers

websocket_urlpatterns = [
    path("ws/usertouser", consumers.UserToUserRealTime.as_asgi()),
    path("ws/batchnotifications", consumers.BatchNotifications.as_asgi()),
    path("ws/institutenotifications", consumers.InstituteNotifications.as_asgi()),
]
