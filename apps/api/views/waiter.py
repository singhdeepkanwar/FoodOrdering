from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from apps.api.permissions import IsWaiterOrAdmin
from apps.api.serializers import OrderSerializer, TableSerializer, TableSessionSerializer
from apps.menu.models import MenuCategory, MenuItem
from apps.api.serializers import MenuCategorySerializer
from apps.orders.models import Order, OrderItem, TableSession
from apps.tables.models import Table


@api_view(["GET"])
@permission_classes([IsWaiterOrAdmin])
def waiter_tables(request):
    restaurant = request.user.restaurant
    tables = Table.objects.filter(restaurant=restaurant, is_active=True)
    data = []
    for table in tables:
        active_session = TableSession.objects.filter(table=table, is_active=True).first()
        pending = Order.objects.filter(
            table=table,
            status__in=[Order.PENDING, Order.CONFIRMED, Order.PREPARING, Order.READY],
        ).count()
        data.append(
            {
                "table": TableSerializer(table, context={"request": request}).data,
                "session": TableSessionSerializer(active_session).data if active_session else None,
                "pending_orders": pending,
            }
        )
    return Response(data)


@api_view(["GET"])
@permission_classes([IsWaiterOrAdmin])
def waiter_table_detail(request, pk):
    restaurant = request.user.restaurant
    try:
        table = Table.objects.get(pk=pk, restaurant=restaurant)
    except Table.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    active_session = TableSession.objects.filter(table=table, is_active=True).first()
    orders = []
    if active_session:
        orders = (
            Order.objects.filter(table_session=active_session)
            .prefetch_related("items__menu_item")
            .order_by("created_at")
        )

    categories = MenuCategory.objects.filter(
        restaurant=restaurant, is_active=True
    ).prefetch_related("items")

    return Response(
        {
            "table": TableSerializer(table, context={"request": request}).data,
            "session": TableSessionSerializer(active_session).data if active_session else None,
            "orders": OrderSerializer(orders, many=True, context={"request": request}).data,
            "categories": MenuCategorySerializer(categories, many=True, context={"request": request}).data,
        }
    )


@api_view(["POST"])
@permission_classes([IsWaiterOrAdmin])
def waiter_add_items(request, pk):
    restaurant = request.user.restaurant
    try:
        table = Table.objects.get(pk=pk, restaurant=restaurant)
    except Table.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    active_session = TableSession.objects.filter(table=table, is_active=True).first()
    cart = request.data.get("cart", [])
    if not cart:
        return Response({"detail": "No items provided."}, status=status.HTTP_400_BAD_REQUEST)

    if not active_session:
        name = (request.data.get("customer_name") or "").strip() or "Walk-in"
        phone = (request.data.get("customer_phone") or "").strip() or "—"
        active_session = TableSession.objects.create(
            table=table, customer_name=name, customer_phone=phone
        )

    order = Order.objects.create(
        restaurant=restaurant,
        table=table,
        table_session=active_session,
        customer_name=active_session.customer_name,
        special_instructions=(request.data.get("special_instructions") or "").strip(),
    )

    added = 0
    for entry in cart:
        try:
            item = MenuItem.objects.get(
                pk=entry["id"], restaurant=restaurant, is_available=True
            )
            qty = max(1, int(entry.get("qty", 1)))
            OrderItem.objects.create(
                order=order, menu_item=item, quantity=qty, unit_price=item.price
            )
            added += 1
        except (MenuItem.DoesNotExist, KeyError, ValueError, TypeError):
            pass

    if added:
        order.calculate_total()
        return Response(OrderSerializer(order, context={"request": request}).data, status=status.HTTP_201_CREATED)

    order.delete()
    return Response(
        {"detail": "No valid items could be added."},
        status=status.HTTP_400_BAD_REQUEST,
    )


@api_view(["POST"])
@permission_classes([IsWaiterOrAdmin])
def waiter_close_table(request, pk):
    restaurant = request.user.restaurant
    try:
        table = Table.objects.get(pk=pk, restaurant=restaurant)
    except Table.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    active_session = TableSession.objects.filter(table=table, is_active=True).first()
    if not active_session:
        return Response({"detail": "Table is already vacant."}, status=status.HTTP_400_BAD_REQUEST)

    active_session.is_active = False
    active_session.save(update_fields=["is_active"])
    return Response({"detail": "Table closed."})


@api_view(["POST"])
@permission_classes([IsWaiterOrAdmin])
def mark_served(request, pk):
    restaurant = request.user.restaurant
    try:
        order = Order.objects.get(pk=pk, restaurant=restaurant)
    except Order.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if order.status != Order.READY:
        return Response(
            {"detail": "Order must be READY before it can be marked served."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    order.status = Order.SERVED
    order.save(update_fields=["status", "updated_at"])
    return Response(OrderSerializer(order, context={"request": request}).data)
