from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from apps.api.permissions import IsRestaurantAdmin
from apps.api.serializers import MenuCategorySerializer, MenuItemSerializer, MenuItemReadSerializer
from apps.menu.models import MenuCategory, MenuItem


def _check_item_limit(restaurant):
    sub = restaurant.active_subscription
    if not sub:
        return False
    limit = sub.plan.max_menu_items
    return limit == -1 or restaurant.menu_items.count() < limit


# ── Categories ────────────────────────────────────────────────────────────────

@api_view(["GET", "POST"])
@permission_classes([IsRestaurantAdmin])
def category_list_create(request):
    restaurant = request.user.restaurant
    if request.method == "GET":
        cats = MenuCategory.objects.filter(restaurant=restaurant).prefetch_related("items")
        return Response(MenuCategorySerializer(cats, many=True, context={"request": request}).data)

    serializer = MenuCategorySerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(restaurant=restaurant)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "PUT", "DELETE"])
@permission_classes([IsRestaurantAdmin])
def category_detail(request, pk):
    restaurant = request.user.restaurant
    try:
        cat = MenuCategory.objects.get(pk=pk, restaurant=restaurant)
    except MenuCategory.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        return Response(MenuCategorySerializer(cat, context={"request": request}).data)
    if request.method == "PUT":
        serializer = MenuCategorySerializer(cat, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    cat.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


# ── Items ─────────────────────────────────────────────────────────────────────

@api_view(["GET", "POST"])
@permission_classes([IsRestaurantAdmin])
def item_list_create(request):
    restaurant = request.user.restaurant
    if request.method == "GET":
        items = MenuItem.objects.filter(restaurant=restaurant).select_related("category")
        return Response(MenuItemReadSerializer(items, many=True, context={"request": request}).data)

    if not _check_item_limit(restaurant):
        return Response(
            {"detail": "Menu item limit reached. Please upgrade your plan."},
            status=status.HTTP_403_FORBIDDEN,
        )
    serializer = MenuItemSerializer(data=request.data, context={"request": request})
    if serializer.is_valid():
        serializer.save(restaurant=restaurant)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "PUT", "DELETE"])
@permission_classes([IsRestaurantAdmin])
def item_detail(request, pk):
    restaurant = request.user.restaurant
    try:
        item = MenuItem.objects.get(pk=pk, restaurant=restaurant)
    except MenuItem.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        return Response(MenuItemReadSerializer(item, context={"request": request}).data)
    if request.method == "PUT":
        serializer = MenuItemSerializer(
            item, data=request.data, partial=True, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(MenuItemReadSerializer(item, context={"request": request}).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    item.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["POST"])
@permission_classes([IsRestaurantAdmin])
def item_toggle(request, pk):
    restaurant = request.user.restaurant
    try:
        item = MenuItem.objects.get(pk=pk, restaurant=restaurant)
    except MenuItem.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    item.is_available = not item.is_available
    item.save(update_fields=["is_available"])
    return Response({"is_available": item.is_available})
