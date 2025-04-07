from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import PostViewSet, CategoryViewSet, TagViewSet, CommentViewSet, search_posts_api, author_posts_api

router = DefaultRouter()
router.register(r'posts', PostViewSet, basename='post')
router.register(r'categories', CategoryViewSet)
router.register(r'tags', TagViewSet)
router.register(r'comments', CommentViewSet, basename='comment')

urlpatterns = [
    path('', include(router.urls)),
    path('search/', search_posts_api, name='api-search-posts'),
    path('author/<str:author_name>/', author_posts_api, name='api-author-posts'),
]