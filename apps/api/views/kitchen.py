from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from apps.api.permissions import IsKitchenOrAdmin
from apps.api.serializers import OrderSerializer
from apps.orders.models import Order

ACTIVE_STATUSES = [Order.PENDING, Order.CONFIRMED, Order.PREPARING, Order.READY]

ALLOWED_TRANSITIONS = {
    Order.PENDING: Order.CONFIRMED,
    Order.CONFIRMED: Order.PREPARING,
    Order.PREPARING: Order.READY,
}


@api_view(["GET"])
@permission_classes([IsKitchenOrAdmin])
def kitchen_orders(request):
    restaurant = request.user.restaurant
    orders = (
        Order.objects.filter(restaurant=restaurant, status__in=ACTIVE_STATUSES)
        .select_related("table")
        .prefetch_related("items__menu_item")
        .order_by("created_at")
    )
    columns = {s: [] for s in ACTIVE_STATUSES}
    for order in orders:
        columns[order.status].append(
            OrderSerializer(order, context={"request": request}).data
        )
    return Response({"columns": columns})


@api_view(["POST"])
@permission_classes([IsKitchenOrAdmin])
def advance_order(request, pk):
    restaurant = request.user.restaurant
    try:
        order = Order.objects.get(pk=pk, restaurant=restaurant)
    except Order.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    next_status = ALLOWED_TRANSITIONS.get(order.status)
    if not next_status:
        return Response(
            {"detail": "Cannot advance from current status."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    order.status = next_status
    order.save(update_fields=["status", "updated_at"])
    return Response(OrderSerializer(order, context={"request": request}).data)


@api_view(["POST"])
@permission_classes([IsKitchenOrAdmin])
def cancel_order(request, pk):
    restaurant = request.user.restaurant
    try:
        order = Order.objects.get(pk=pk, restaurant=restaurant)
    except Order.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if order.status in (Order.SERVED, Order.CANCELLED):
        return Response(
            {"detail": "Cannot cancel a served or already cancelled order."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    order.status = Order.CANCELLED
    order.save(update_fields=["status", "updated_at"])
    return Response(OrderSerializer(order, context={"request": request}).data)
