from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.api.serializers import (
    CustomerMenuCategorySerializer,
    CustomerSessionSerializer,
    OrderSerializer,
)
from apps.menu.models import MenuCategory, MenuItem
from apps.orders.models import Order, OrderItem, TableSession
from apps.tables.models import Table
from apps.tenants.models import Restaurant


def _get_table(qr_token):
    try:
        return Table.objects.select_related("restaurant").get(qr_token=qr_token, is_active=True)
    except Table.DoesNotExist:
        return None


@api_view(["GET"])
@permission_classes([AllowAny])
def customer_menu(request, qr_token):
    table = _get_table(qr_token)
    if not table:
        return Response({"detail": "Table not found."}, status=status.HTTP_404_NOT_FOUND)

    restaurant = table.restaurant
    if not restaurant.is_active:
        return Response({"detail": "Restaurant is closed."}, status=status.HTTP_403_FORBIDDEN)

    categories = MenuCategory.objects.filter(
        restaurant=restaurant, is_active=True
    ).prefetch_related("items")

    return Response(
        {
            "restaurant": {
                "name": restaurant.name,
                "logo": request.build_absolute_uri(restaurant.logo.url) if restaurant.logo else None,
                "currency": restaurant.currency,
            },
            "table": {"id": table.pk, "name": table.name},
            "categories": CustomerMenuCategorySerializer(
                categories, many=True, context={"request": request}
            ).data,
        }
    )


@api_view(["POST"])
@permission_classes([AllowAny])
def customer_checkin(request, qr_token):
    """Create or retrieve a TableSession. Returns session_id to store in localStorage."""
    table = _get_table(qr_token)
    if not table:
        return Response({"detail": "Table not found."}, status=status.HTTP_404_NOT_FOUND)

    name = (request.data.get("customer_name") or "").strip()
    phone = (request.data.get("customer_phone") or "").strip()

    if not name or not phone:
        return Response(
            {"detail": "Name and phone number are required."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    if len(phone) < 10:
        return Response(
            {"detail": "Please enter a valid phone number."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Relink if same phone already has an active session at this table
    existing = TableSession.objects.filter(
        table=table, customer_phone=phone, is_active=True
    ).first()

    if existing:
        ts = existing
    else:
        ts = TableSession.objects.create(
            table=table, customer_name=name, customer_phone=phone
        )

    return Response({"session_id": ts.pk, "customer_name": ts.customer_name}, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([AllowAny])
def customer_session(request, qr_token):
    """Return the current session state + all orders for this sitting."""
    table = _get_table(qr_token)
    if not table:
        return Response({"detail": "Table not found."}, status=status.HTTP_404_NOT_FOUND)

    session_id = request.headers.get("X-Session-Id") or request.GET.get("session_id")
    if not session_id:
        return Response({"detail": "No session."}, status=status.HTTP_401_UNAUTHORIZED)

    try:
        ts = TableSession.objects.get(pk=session_id, table=table, is_active=True)
    except TableSession.DoesNotExist:
        return Response({"detail": "Session expired or not found."}, status=status.HTTP_401_UNAUTHORIZED)

    return Response(CustomerSessionSerializer(ts, context={"request": request}).data)


@api_view(["POST"])
@permission_classes([AllowAny])
def customer_place_order(request, qr_token):
    table = _get_table(qr_token)
    if not table:
        return Response({"detail": "Table not found."}, status=status.HTTP_404_NOT_FOUND)

    session_id = request.headers.get("X-Session-Id") or request.data.get("session_id")
    if not session_id:
        return Response({"detail": "No session."}, status=status.HTTP_401_UNAUTHORIZED)

    try:
        ts = TableSession.objects.get(pk=session_id, table=table, is_active=True)
    except TableSession.DoesNotExist:
        return Response({"detail": "Session expired."}, status=status.HTTP_401_UNAUTHORIZED)

    cart = request.data.get("cart", [])
    if not cart:
        return Response({"detail": "Cart is empty."}, status=status.HTTP_400_BAD_REQUEST)

    restaurant = table.restaurant
    order = Order.objects.create(
        restaurant=restaurant,
        table=table,
        table_session=ts,
        customer_name=ts.customer_name,
        special_instructions=(request.data.get("special_instructions") or "").strip(),
    )

    for entry in cart:
        try:
            item = MenuItem.objects.get(pk=entry["id"], restaurant=restaurant, is_available=True)
            qty = max(1, int(entry.get("qty", 1)))
            OrderItem.objects.create(
                order=order, menu_item=item, quantity=qty, unit_price=item.price
            )
        except (MenuItem.DoesNotExist, KeyError, ValueError, TypeError):
            pass

    order.calculate_total()
    return Response(OrderSerializer(order, context={"request": request}).data, status=status.HTTP_201_CREATED)


@api_view(["GET"])
@permission_classes([AllowAny])
def customer_track_order(request, qr_token, order_id):
    table = _get_table(qr_token)
    if not table:
        return Response({"detail": "Table not found."}, status=status.HTTP_404_NOT_FOUND)

    try:
        order = Order.objects.get(pk=order_id, table=table)
    except Order.DoesNotExist:
        return Response({"detail": "Order not found."}, status=status.HTTP_404_NOT_FOUND)

    return Response(OrderSerializer(order, context={"request": request}).data)
