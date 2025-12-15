from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
from user.v1.views import CustomObtainTokenPairView, DecodeJwtTokenView

app_name = "auth"

urlpatterns = [
    path("login/", CustomObtainTokenPairView.as_view(), name="login"),
    path("token/refresh/", TokenRefreshView.as_view(), name="refresh-token"),
    path("token/verify/", TokenVerifyView.as_view(), name="verify-token"),
    path("token/decode/", DecodeJwtTokenView.as_view(), name="decode-jwt-token"),
    # path('token/', CreateTokenView.as_view(), name='tokens'),
]
