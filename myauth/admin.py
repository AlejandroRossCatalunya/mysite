from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest

from .models import Profile

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = "pk", "user", "bio", "avatar"
    list_display_links = "pk", "user"
    fieldsets = [
        ("Images", {
            "fields": ("avatar",)
        }),
    ]
