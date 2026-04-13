import json
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count
from django.db.models.functions import TruncDay, ExtractHour
from django.utils import timezone
from datetime import timedelta

from apps.orders.models import Order, OrderItem
from apps.billing.models import Subscription


@login_required
def analytics_dashboard(request):
    restaurant = request.user.restaurant
    subscription = getattr(restaurant, "subscription", None)

    # Gate analytics behind plan
    if not subscription or not subscription.plan.has_analytics:
        return render(request, "dashboard/analytics/upgrade.html")

    today = timezone.now()
    thirty_days_ago = today - timedelta(days=30)

    # Revenue by day (last 30 days)
    revenue_qs = (
        Order.objects.filter(
            restaurant=restaurant,
            status=Order.SERVED,
            created_at__gte=thirty_days_ago,
        )
        .annotate(day=TruncDay("created_at"))
        .values("day")
        .annotate(revenue=Sum("total_amount"))
        .order_by("day")
    )
    revenue_labels = [r["day"].strftime("%d %b") for r in revenue_qs]
    revenue_data = [float(r["revenue"]) for r in revenue_qs]

    # Top 10 selling items
    top_items_qs = (
        OrderItem.objects.filter(order__restaurant=restaurant, order__status=Order.SERVED)
        .values("menu_item__name")
        .annotate(total_qty=Sum("quantity"))
        .order_by("-total_qty")[:10]
    )
    top_item_labels = [i["menu_item__name"] for i in top_items_qs]
    top_item_data = [i["total_qty"] for i in top_items_qs]

    # Peak hours (orders per hour of day, last 30 days)
    peak_qs = (
        Order.objects.filter(restaurant=restaurant, created_at__gte=thirty_days_ago)
        .annotate(hour=ExtractHour("created_at"))
        .values("hour")
        .annotate(count=Count("id"))
        .order_by("hour")
    )
    hour_map = {r["hour"]: r["count"] for r in peak_qs}
    peak_labels = [f"{h:02d}:00" for h in range(24)]
    peak_data = [hour_map.get(h, 0) for h in range(24)]

    # Summary stats
    total_revenue = sum(revenue_data)
    total_orders = Order.objects.filter(restaurant=restaurant, status=Order.SERVED).count()
    avg_order_value = round(total_revenue / total_orders, 2) if total_orders else 0

    context = {
        "revenue_labels": json.dumps(revenue_labels),
        "revenue_data": json.dumps(revenue_data),
        "top_item_labels": json.dumps(top_item_labels),
        "top_item_data": json.dumps(top_item_data),
        "peak_labels": json.dumps(peak_labels),
        "peak_data": json.dumps(peak_data),
        "total_revenue": total_revenue,
        "total_orders": total_orders,
        "avg_order_value": avg_order_value,
    }
    return render(request, "dashboard/analytics/dashboard.html", context)
