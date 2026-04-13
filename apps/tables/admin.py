from django.contrib import admin
from .models import Table


@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ("name", "restaurant", "qr_token", "is_active")
    readonly_fields = ("qr_token", "qr_image")
