from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import auth, dashboard, menu, tables, orders, kitchen, waiter, customer, analytics, billing

urlpatterns = [
    # ── Auth ─────────────────────────────────────────────────────────────────
    path("auth/token/", TokenObtainPairView.as_view(), name="token_obtain"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("auth/register/", auth.register, name="register"),
    path("auth/me/", auth.me, name="me"),

    # ── Dashboard ─────────────────────────────────────────────────────────────
    path("dashboard/", dashboard.dashboard_home, name="dashboard"),

    # ── Menu ──────────────────────────────────────────────────────────────────
    path("menu/categories/", menu.category_list_create, name="category-list"),
    path("menu/categories/<int:pk>/", menu.category_detail, name="category-detail"),
    path("menu/items/", menu.item_list_create, name="item-list"),
    path("menu/items/<int:pk>/", menu.item_detail, name="item-detail"),
    path("menu/items/<int:pk>/toggle/", menu.item_toggle, name="item-toggle"),

    # ── Tables ────────────────────────────────────────────────────────────────
    path("tables/", tables.table_list_create, name="table-list"),
    path("tables/<int:pk>/", tables.table_detail, name="table-detail"),
    path("tables/<int:pk>/qr/", tables.table_regenerate_qr, name="table-qr"),

    # ── Orders (dashboard) ────────────────────────────────────────────────────
    path("orders/", orders.order_list, name="order-list"),
    path("orders/<int:pk>/mark-paid/", orders.mark_paid, name="order-mark-paid"),

    # ── Kitchen ───────────────────────────────────────────────────────────────
    path("kitchen/orders/", kitchen.kitchen_orders, name="kitchen-orders"),
    path("kitchen/orders/<int:pk>/advance/", kitchen.advance_order, name="kitchen-advance"),
    path("kitchen/orders/<int:pk>/cancel/", kitchen.cancel_order, name="kitchen-cancel"),

    # ── Waiter ────────────────────────────────────────────────────────────────
    path("waiter/tables/", waiter.waiter_tables, name="waiter-tables"),
    path("waiter/tables/<int:pk>/", waiter.waiter_table_detail, name="waiter-table-detail"),
    path("waiter/tables/<int:pk>/add-items/", waiter.waiter_add_items, name="waiter-add-items"),
    path("waiter/orders/<int:pk>/mark-served/", waiter.mark_served, name="waiter-mark-served"),

    # ── Customer (public, no auth) ────────────────────────────────────────────
    path("customer/<uuid:qr_token>/menu/", customer.customer_menu, name="customer-menu"),
    path("customer/<uuid:qr_token>/checkin/", customer.customer_checkin, name="customer-checkin"),
    path("customer/<uuid:qr_token>/session/", customer.customer_session, name="customer-session"),
    path("customer/<uuid:qr_token>/order/", customer.customer_place_order, name="customer-order"),
    path("customer/<uuid:qr_token>/order/<int:order_id>/", customer.customer_track_order, name="customer-track"),

    # ── Analytics ─────────────────────────────────────────────────────────────
    path("analytics/", analytics.analytics_dashboard, name="analytics"),

    # ── Billing ───────────────────────────────────────────────────────────────
    path("billing/", billing.billing_dashboard, name="billing"),
    path("billing/change-plan/<int:plan_id>/", billing.change_plan, name="billing-change-plan"),
]
