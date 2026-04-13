from django.contrib import admin
from .models import SubscriptionPlan, Subscription, Invoice


@admin.register(SubscriptionPlan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ("name", "price_monthly", "max_tables", "max_menu_items", "has_analytics")


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("restaurant", "plan", "status", "starts_at", "expires_at")
    list_filter = ("status", "plan")


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ("pk", "subscription", "amount", "status", "issued_at", "paid_at")
