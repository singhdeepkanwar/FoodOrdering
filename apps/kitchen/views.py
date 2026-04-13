from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from apps.orders.models import Order


# Kitchen only handles up to READY — waiter takes it from READY → SERVED
ACTIVE_STATUSES = [Order.PENDING, Order.CONFIRMED, Order.PREPARING, Order.READY]

ALLOWED_TRANSITIONS = {
    Order.PENDING: Order.CONFIRMED,
    Order.CONFIRMED: Order.PREPARING,
    Order.PREPARING: Order.READY,
    # READY → SERVED is the waiter's responsibility
}


@login_required
def kitchen_board(request):
    restaurant = request.user.restaurant
    return render(request, "kitchen/board.html", {"restaurant": restaurant})


@login_required
def orders_partial(request):
    restaurant = request.user.restaurant
    orders = (
        Order.objects.filter(restaurant=restaurant, status__in=ACTIVE_STATUSES)
        .select_related("table")
        .prefetch_related("items__menu_item")
        .order_by("created_at")
    )
    columns = {
        Order.PENDING: [],
        Order.CONFIRMED: [],
        Order.PREPARING: [],
        Order.READY: [],
    }
    for order in orders:
        if order.status in columns:
            columns[order.status].append(order)
    return render(request, "kitchen/partials/board_columns.html", {
        "columns": columns,
        "transitions": ALLOWED_TRANSITIONS,
    })


@login_required
@require_POST
def update_order_status(request, order_id):
    restaurant = request.user.restaurant
    order = get_object_or_404(Order, pk=order_id, restaurant=restaurant)
    next_status = ALLOWED_TRANSITIONS.get(order.status)
    if next_status:
        order.status = next_status
        order.save(update_fields=["status", "updated_at"])
    # Re-render the board
    return orders_partial(request)


@login_required
@require_POST
def cancel_order(request, order_id):
    restaurant = request.user.restaurant
    order = get_object_or_404(Order, pk=order_id, restaurant=restaurant)
    if order.status not in (Order.SERVED, Order.CANCELLED):
        order.status = Order.CANCELLED
        order.save(update_fields=["status", "updated_at"])
    return orders_partial(request)


