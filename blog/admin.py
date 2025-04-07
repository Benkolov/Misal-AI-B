from django.contrib import admin
from .models import Post, Tag, Comment, Category


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('id','title', 'get_author', 'status', 'published_at')
    list_filter = ('status', 'created_at', 'published_at')
    search_fields = ('title', 'content', 'author', 'author_user__username', 'author_user__email')
    prepopulated_fields = {'slug': ('title',)}

    def get_author(self, obj):
        if obj.author_user:
            return obj.author_user.username or obj.author_user.email
        return obj.author or 'Anonymous'
    get_author.short_description = 'Author'

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id','name')
    search_fields = ('name',)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('get_author', 'post', 'created_at', 'active')
    list_filter = ('active', 'created_at')
    search_fields = ('name', 'email', 'author_user__username', 'author_user__email', 'body')

    def get_author(self, obj):
        if obj.author_user:
            return obj.author_user.username or obj.author_user.email
        return obj.name or 'Anonymous'
    get_author.short_description = 'Author'

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
