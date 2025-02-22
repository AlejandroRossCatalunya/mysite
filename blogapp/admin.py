from django.contrib import admin

from .models import RSSArticle


@admin.register(RSSArticle)
class RSSArticleAdmin(admin.ModelAdmin):
    list_display = "id", "title", "body", "published_at"
