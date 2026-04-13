from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import Order, TableSession


@login_required
def order_list(request):
    restaurant = request.user.restaurant
    status_filter = request.GET.get("status", "")
    payment_filter = request.GET.get("payment", "")
    orders = Order.objects.filter(restaurant=restaurant).select_related("table", "table_session")
    if status_filter:
        orders = orders.filter(status=status_filter)
    if payment_filter:
        orders = orders.filter(payment_status=payment_filter)
    return render(request, "dashboard/orders/list.html", {
        "orders": orders,
        "status_filter": status_filter,
        "payment_filter": payment_filter,
        "statuses": Order.STATUS_CHOICES,
    })


@login_required
@require_POST
def mark_paid(request, order_id):
    restaurant = request.user.restaurant
    order = get_object_or_404(Order, pk=order_id, restaurant=restaurant)
    if order.payment_status == Order.UNPAID:
        order.payment_status = Order.PAID
        order.paid_at = timezone.now()
        order.save(update_fields=["payment_status", "paid_at", "updated_at"])

        # If all orders in this table session are now paid → close the session
        # so the next customer gets a clean check-in
        if order.table_session:
            ts = order.table_session
            all_paid = not ts.orders.filter(payment_status=Order.UNPAID).exists()
            if all_paid:
                ts.is_active = False
                ts.save(update_fields=["is_active"])

    messages.success(request, f"Order #{order.pk} marked as paid.")
    return render(request, "dashboard/orders/list.html", {
        "orders": Order.objects.filter(restaurant=restaurant).select_related("table", "table_session"),
        "status_filter": "",
        "payment_filter": "",
        "statuses": Order.STATUS_CHOICES,
    })
