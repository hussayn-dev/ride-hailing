from django.urls import include, path
from rest_framework.routers import DefaultRouter
from user.v1.views import UserVieSets

app_name = "user"

router = DefaultRouter()
router.register("", UserVieSets)

urlpatterns = [
    path("", include(router.urls)),
]
