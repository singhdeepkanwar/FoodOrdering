from django.contrib import admin
from .models import MenuCategory, MenuItem


@admin.register(MenuCategory)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "restaurant", "display_order", "is_active")


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ("name", "restaurant", "category", "price", "is_veg", "is_available")
    list_filter = ("is_veg", "is_available", "restaurant")
