from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from apps.api.permissions import IsRestaurantAdmin
from apps.api.serializers import TableSerializer
from apps.tables.models import Table


def _check_table_limit(restaurant):
    sub = restaurant.active_subscription
    if not sub:
        return False
    limit = sub.plan.max_tables
    return limit == -1 or restaurant.tables.count() < limit


@api_view(["GET", "POST"])
@permission_classes([IsRestaurantAdmin])
def table_list_create(request):
    restaurant = request.user.restaurant
    if request.method == "GET":
        tables = Table.objects.filter(restaurant=restaurant)
        return Response(TableSerializer(tables, many=True, context={"request": request}).data)

    if not _check_table_limit(restaurant):
        return Response(
            {"detail": "Table limit reached. Please upgrade your plan."},
            status=status.HTTP_403_FORBIDDEN,
        )
    serializer = TableSerializer(data=request.data, context={"request": request})
    if serializer.is_valid():
        table = serializer.save(restaurant=restaurant)
        # Generate QR — URL points to the React frontend
        frontend_url = getattr(settings, "FRONTEND_URL", "").rstrip("/")
        table.generate_qr(frontend_url)
        table.save()
        return Response(
            TableSerializer(table, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "PUT", "DELETE"])
@permission_classes([IsRestaurantAdmin])
def table_detail(request, pk):
    restaurant = request.user.restaurant
    try:
        table = Table.objects.get(pk=pk, restaurant=restaurant)
    except Table.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        return Response(TableSerializer(table, context={"request": request}).data)
    if request.method == "PUT":
        serializer = TableSerializer(table, data=request.data, partial=True, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response(TableSerializer(table, context={"request": request}).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    table.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["POST"])
@permission_classes([IsRestaurantAdmin])
def table_regenerate_qr(request, pk):
    restaurant = request.user.restaurant
    try:
        table = Table.objects.get(pk=pk, restaurant=restaurant)
    except Table.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    frontend_url = getattr(settings, "FRONTEND_URL", "").rstrip("/")
    table.generate_qr(frontend_url)
    table.save()
    return Response(TableSerializer(table, context={"request": request}).data)
