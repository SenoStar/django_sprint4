from django.contrib import admin
from .models import Category, Location, Post


class PostAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'category',
        'is_published',
        'author',
        'location',
        'created_at'
    )
    list_editable = (
        'is_published',
        'category',
        'author',
        'location'
    )
    search_fields = ('title',)
    list_filter = ('author', 'location', 'category', 'created_at')
    list_display_links = ('title',)


admin.site.register(Category)
admin.site.register(Location)
admin.site.register(Post, PostAdmin)
