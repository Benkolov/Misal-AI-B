from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import Post, Category, Tag, Comment
from .serializers import PostSerializer, CategorySerializer, TagSerializer, CommentSerializer
from .permissions import IsStaffOrReadOnly
from .utils import render_markdown

class PostViewSet(viewsets.ModelViewSet):
    serializer_class = PostSerializer
    lookup_field = 'slug'
    permission_classes = [IsStaffOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'content', 'excerpt', 'author', 'author_user__username', 'author_user__email']
    pagination_class = None  # Ще използваме глобалната пагинация

    def get_queryset(self):
        # Филтрираме по статус и категория, ако е подадена
        queryset = Post.objects.all()

        # Филтрираме по статус
        status = self.request.query_params.get('status', 'published')
        if status:
            queryset = queryset.filter(status=status)

        # Филтрираме по категория
        category_id = self.request.query_params.get('category', None)
        if category_id:
            queryset = queryset.filter(category_id=category_id)

        # Филтрираме по таг
        tag_id = self.request.query_params.get('tag', None)
        if tag_id:
            queryset = queryset.filter(tags__id=tag_id)

        return queryset.order_by('-published_at')

    def perform_create(self, serializer):
        serializer.save(author=self.request.user.username, author_user=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        # Проверяваме дали публикацията е публикувана, освен ако потребителят не е staff
        instance = self.get_object()
        if instance.status != 'published' and not request.user.is_staff:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        instance.content = render_markdown(instance.content)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def increment_views(self, request, slug=None):
        post = self.get_object()
        post.views_count += 1
        post.save()
        return Response({'views_count': post.views_count})

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'
    permission_classes = [IsStaffOrReadOnly]

    @action(detail=True, methods=['get'])
    def posts(self, request, slug=None):
        category = self.get_object()
        posts = Post.objects.filter(category=category, status='published')

        # Добавяме пагинация
        page = self.paginate_queryset(posts)
        if page is not None:
            serializer = PostSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        serializer.save()

class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsStaffOrReadOnly]
    pagination_class = None  # Изключваме pagination за таговете

    @action(detail=True, methods=['get'])
    def posts(self, request, pk=None):
        tag = self.get_object()
        posts = Post.objects.filter(tags=tag, status='published')

        # Добавяме пагинация
        page = self.paginate_queryset(posts)
        if page is not None:
            serializer = PostSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)

class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = None  # Ще използваме глобалната пагинация

    def get_queryset(self):
        queryset = Comment.objects.filter(active=True)
        post_id = self.request.query_params.get('post', None)
        if post_id is not None:
            queryset = queryset.filter(post_id=post_id)

        # Филтрираме по автор, ако е подаден
        author_id = self.request.query_params.get('author', None)
        if author_id is not None:
            queryset = queryset.filter(author_user_id=author_id)

        # Филтрираме по име, ако е подадено
        name = self.request.query_params.get('name', None)
        if name is not None:
            queryset = queryset.filter(name__icontains=name)

        return queryset.order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(author_user=self.request.user)

    def perform_update(self, serializer):
        if self.request.user == serializer.instance.author_user or self.request.user.is_staff:
            serializer.save()
        else:
            raise permissions.PermissionDenied("You don't have permission to edit this comment.")

    def perform_destroy(self, instance):
        if self.request.user == instance.author_user or self.request.user.is_staff:
            instance.delete()
        else:
            raise permissions.PermissionDenied("You don't have permission to delete this comment.")


@api_view(['GET'])
def search_posts_api(request):
    """
    API ендпойнт за търсене на публикации
    """
    query = request.query_params.get('q', '')
    if query:
        posts = Post.objects.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(excerpt__icontains=query) |
            Q(author_user__username__icontains=query) |
            Q(author_user__email__icontains=query) |
            Q(author__icontains=query),
            status='published'
        ).order_by('-published_at')
    else:
        posts = Post.objects.none()

    # Добавяме пагинация
    from rest_framework.pagination import PageNumberPagination
    paginator = PageNumberPagination()
    paginator.page_size = 10
    result_page = paginator.paginate_queryset(posts, request)
    serializer = PostSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)


@api_view(['GET'])
def author_posts_api(request, author_name):
    """
    API ендпойнт за публикации по автор
    """
    # Търсим по потребителско име, имейл или полето author
    posts = Post.objects.filter(
        Q(author_user__username__iexact=author_name) |
        Q(author_user__email__iexact=author_name) |
        Q(author__iexact=author_name),
        status='published'
    ).order_by('-published_at')

    # Добавяме пагинация
    from rest_framework.pagination import PageNumberPagination
    paginator = PageNumberPagination()
    paginator.page_size = 10
    result_page = paginator.paginate_queryset(posts, request)
    serializer = PostSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)