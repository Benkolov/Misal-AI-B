from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import UserViewSet, CustomAuthToken

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
    path('login/', CustomAuthToken.as_view(), name='api_token_auth'),
]
