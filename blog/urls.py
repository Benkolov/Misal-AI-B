from django.urls import path
from blog.views import post_list, post_detail, post_create, tag_create, category_create, category_list, category_detail, \
    post_edit, author_posts, search_posts

urlpatterns = [
    path('', post_list, name='post list'),
    path('search/', search_posts, name='search posts'),
    path('create/', post_create, name='post create'),
    path('category/create/', category_create, name='category create'),
    path('tag/create/', tag_create, name='tag create'),
    path('categories/', category_list, name='category list'),
    path('author/<str:author_name>/', author_posts, name='author posts'),
    path('category/<slug:slug>/', category_detail, name='category detail'),
    path('<slug:slug>/', post_detail, name='post detail'),
    path('<slug:slug>/edit/', post_edit, name='post edit'),

]
