from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from apps.api.permissions import IsRestaurantAdmin
from apps.api.serializers import OrderSerializer
from apps.orders.models import Order


@api_view(["GET"])
@permission_classes([IsRestaurantAdmin])
def order_list(request):
    restaurant = request.user.restaurant
    qs = Order.objects.filter(restaurant=restaurant).select_related("table", "table_session").prefetch_related("items__menu_item")

    status_filter = request.GET.get("status", "")
    payment_filter = request.GET.get("payment", "")
    if status_filter:
        qs = qs.filter(status=status_filter)
    if payment_filter:
        qs = qs.filter(payment_status=payment_filter)

    return Response(OrderSerializer(qs, many=True, context={"request": request}).data)


@api_view(["POST"])
@permission_classes([IsRestaurantAdmin])
def mark_paid(request, pk):
    restaurant = request.user.restaurant
    try:
        order = Order.objects.get(pk=pk, restaurant=restaurant)
    except Order.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if order.payment_status == Order.UNPAID:
        order.payment_status = Order.PAID
        order.paid_at = timezone.now()
        order.save(update_fields=["payment_status", "paid_at", "updated_at"])

        # Close session if all orders in this sitting are paid
        if order.table_session:
            ts = order.table_session
            if not ts.orders.filter(payment_status=Order.UNPAID).exists():
                ts.is_active = False
                ts.save(update_fields=["is_active"])

    return Response(OrderSerializer(order, context={"request": request}).data)
