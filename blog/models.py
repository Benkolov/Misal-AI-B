from django.db import models
from django.utils.text import slugify
from django.utils.timezone import now
from django.conf import settings
from unidecode import unidecode


class Post(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True, null=True)
    content = models.TextField()
    excerpt = models.TextField(blank=True, null=True, help_text="Кратко описание на публикацията")
    author = models.CharField(max_length=100)
    author_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name='posts', null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    published_at = models.DateTimeField(default=now, blank=True, null=True)
    tags = models.ManyToManyField('Tag', related_name='posts', blank=True)
    featured_image = models.ImageField(upload_to='featured_images/', blank=True, null=True)
    views_count = models.PositiveIntegerField(default=0)
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True, blank=True, related_name='posts')

    class Meta:
        ordering = ['-published_at']

    def save(self, *args, **kwargs):
        # Първо запазваме обекта, за да получим ID, ако е нов запис
        is_new = self.pk is None
        super().save(*args, **kwargs)

        # Генерираме slug само ако е необходимо
        if not self.slug or is_new:
            transliterated_title = unidecode(self.title)
            self.slug = slugify(f"{transliterated_title}-{self.id}", allow_unicode=True)
            # Запазваме отново само ако сме променили slug
            super().save(update_fields=['slug'])

    def __str__(self):
        return self.title


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True, null=True)

    def save(self, *args, **kwargs):
        # Първо запазваме обекта, за да получим ID, ако е нов запис
        is_new = self.pk is None
        super().save(*args, **kwargs)

        # Генерираме slug само ако е необходимо
        if not self.slug or is_new:
            transliterated_title = unidecode(self.name)
            self.slug = slugify(f"{transliterated_title}-{self.id}", allow_unicode=True)
            # Запазваме отново само ако сме променили slug
            super().save(update_fields=['slug'])

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Comment(models.Model):
    post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='comments')
    name = models.CharField(max_length=80, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    author_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name='comments', null=True, blank=True)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        author_info = self.name or "Anonymous"
        if self.author_user:
            author_info = self.author_user.username or self.author_user.email
        return f"Comment by {author_info} on {self.post}"
