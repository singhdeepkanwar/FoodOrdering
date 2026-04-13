from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from apps.orders.models import Order


@login_required
def dashboard_home(request):
    restaurant = request.user.restaurant
    if not restaurant:
        # Super-admins or manually created users with no restaurant — show a clear error page
        # Do NOT redirect to login (that creates a redirect loop since login bounces
        # authenticated users back here)
        return render(request, "dashboard/no_restaurant.html", {"user": request.user})

    recent_orders = Order.objects.filter(
        restaurant=restaurant
    ).select_related("table")[:10]

    context = {
        "restaurant": restaurant,
        "recent_orders": recent_orders,
        "total_tables": restaurant.tables.filter(is_active=True).count(),
        "total_items": restaurant.menu_items.filter(is_available=True).count(),
        "pending_orders": restaurant.orders.filter(status=Order.PENDING).count(),
    }
    return render(request, "dashboard/home.html", context)
