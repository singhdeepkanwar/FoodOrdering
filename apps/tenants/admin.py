from django.contrib import admin
from .models import Restaurant


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "owner", "city", "is_active", "created_at")
    list_filter = ("is_active",)
    prepopulated_fields = {"slug": ("name",)}
