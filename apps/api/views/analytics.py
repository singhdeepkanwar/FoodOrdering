from datetime import timedelta

from django.db.models import Count, Sum
from django.db.models.functions import ExtractHour, TruncDay
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status

from apps.api.permissions import IsRestaurantAdmin
from apps.orders.models import Order, OrderItem


@api_view(["GET"])
@permission_classes([IsRestaurantAdmin])
def analytics_dashboard(request):
    restaurant = request.user.restaurant
    sub = getattr(restaurant, "subscription", None)

    if not sub or not sub.plan.has_analytics:
        return Response(
            {"detail": "Analytics not available on your current plan."},
            status=status.HTTP_403_FORBIDDEN,
        )

    today = timezone.now()
    thirty_days_ago = today - timedelta(days=30)

    revenue_qs = (
        Order.objects.filter(
            restaurant=restaurant, status=Order.SERVED, created_at__gte=thirty_days_ago
        )
        .annotate(day=TruncDay("created_at"))
        .values("day")
        .annotate(revenue=Sum("total_amount"))
        .order_by("day")
    )

    top_items_qs = (
        OrderItem.objects.filter(order__restaurant=restaurant, order__status=Order.SERVED)
        .values("menu_item__name")
        .annotate(total_qty=Sum("quantity"))
        .order_by("-total_qty")[:10]
    )

    peak_qs = (
        Order.objects.filter(restaurant=restaurant, created_at__gte=thirty_days_ago)
        .annotate(hour=ExtractHour("created_at"))
        .values("hour")
        .annotate(count=Count("id"))
        .order_by("hour")
    )
    hour_map = {r["hour"]: r["count"] for r in peak_qs}

    revenue_data = [float(r["revenue"]) for r in revenue_qs]
    total_revenue = sum(revenue_data)
    total_orders = Order.objects.filter(restaurant=restaurant, status=Order.SERVED).count()

    return Response(
        {
            "revenue": {
                "labels": [r["day"].strftime("%d %b") for r in revenue_qs],
                "data": revenue_data,
            },
            "top_items": {
                "labels": [i["menu_item__name"] for i in top_items_qs],
                "data": [i["total_qty"] for i in top_items_qs],
            },
            "peak_hours": {
                "labels": [f"{h:02d}:00" for h in range(24)],
                "data": [hour_map.get(h, 0) for h in range(24)],
            },
            "summary": {
                "total_revenue": total_revenue,
                "total_orders": total_orders,
                "avg_order_value": round(total_revenue / total_orders, 2) if total_orders else 0,
            },
        }
    )
