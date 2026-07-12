from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenBlacklistView,
)

from django.urls import path, include

from .views import RegisterView

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh_view'),
    path('token/blacklist/', TokenBlacklistView.as_view(), name='token_blacklist_view'),
    path('register/', RegisterView.as_view(), name='register')
]