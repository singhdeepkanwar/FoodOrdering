from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from apps.api.permissions import IsRestaurantStaff
from apps.api.serializers import OrderSerializer
from apps.orders.models import Order


@api_view(["GET"])
@permission_classes([IsRestaurantStaff])
def dashboard_home(request):
    restaurant = request.user.restaurant
    recent_orders = (
        Order.objects.filter(restaurant=restaurant)
        .select_related("table", "table_session")
        .prefetch_related("items__menu_item")[:10]
    )
    return Response(
        {
            "total_tables": restaurant.tables.filter(is_active=True).count(),
            "total_items": restaurant.menu_items.filter(is_available=True).count(),
            "pending_orders": restaurant.orders.filter(status=Order.PENDING).count(),
            "recent_orders": OrderSerializer(
                recent_orders, many=True, context={"request": request}
            ).data,
        }
    )
