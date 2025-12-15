from django.urls import path, include
from rest_framework.routers import DefaultRouter

from trip.v1.views import TripViewSet

app_name = 'trip'

router = DefaultRouter()
router.register('', TripViewSet, basename='trip')
urlpatterns = [
    path('', include(router.urls)),
]
