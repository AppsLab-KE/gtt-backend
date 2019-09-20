from django.contrib import admin
from django.contrib.auth import get_user_model
from posts.models import Category, Post, Comment, Reply, Bookmark
from posts.forms import CategoryForm

User = get_user_model()

class CategoryAdmin(admin.ModelAdmin):
    form = CategoryForm
    list_display = (
        'category_name',
        'resource_key',
        'slug',
    )

class BookmarkAdmin(admin.ModelAdmin):
    list_display = (
        'bookmarked_post',
        'user_that_bookmarked',
    )

admin.site.register(Category, CategoryAdmin)
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Reply)
admin.site.register(Bookmark, BookmarkAdmin)
admin.site.register(User)


