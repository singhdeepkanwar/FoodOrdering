import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST

from apps.tables.models import Table
from apps.menu.models import MenuCategory, MenuItem
from apps.orders.models import Order, OrderItem, TableSession


def waiter_required(view_func):
    """Allow restaurant_admin and waiter roles."""
    @login_required
    def wrapper(request, *args, **kwargs):
        if request.user.role not in ("restaurant_admin", "waiter"):
            messages.error(request, "Access denied.")
            return redirect("accounts:login")
        return view_func(request, *args, **kwargs)
    return wrapper


@waiter_required
def tables_overview(request):
    """Show all active tables with their current open orders."""
    restaurant = request.user.restaurant
    tables = Table.objects.filter(restaurant=restaurant, is_active=True)

    # Attach active orders to each table
    active_statuses = [Order.PENDING, Order.CONFIRMED, Order.PREPARING, Order.READY, Order.SERVED]
    table_data = []
    for table in tables:
        active_session = TableSession.objects.filter(table=table, is_active=True).first()
        pending_orders = Order.objects.filter(
            table=table, status__in=[Order.PENDING, Order.CONFIRMED, Order.PREPARING, Order.READY]
        ).count()
        table_data.append({
            "table": table,
            "session": active_session,
            "pending_orders": pending_orders,
        })

    return render(request, "waiter/tables.html", {"table_data": table_data, "restaurant": restaurant})


@waiter_required
def table_detail(request, table_id):
    """Show all orders for this table's active session; allow adding items + marking served."""
    restaurant = request.user.restaurant
    table = get_object_or_404(Table, pk=table_id, restaurant=restaurant)
    active_session = TableSession.objects.filter(table=table, is_active=True).first()

    orders = []
    if active_session:
        orders = Order.objects.filter(
            table_session=active_session
        ).prefetch_related("items__menu_item").order_by("created_at")

    categories = MenuCategory.objects.filter(
        restaurant=restaurant, is_active=True
    ).prefetch_related("items")

    return render(request, "waiter/table_detail.html", {
        "table": table,
        "session": active_session,
        "orders": orders,
        "categories": categories,
        "restaurant": restaurant,
    })


@waiter_required
@require_POST
def mark_served(request, order_id):
    restaurant = request.user.restaurant
    order = get_object_or_404(Order, pk=order_id, restaurant=restaurant)
    if order.status == Order.READY:
        order.status = Order.SERVED
        order.save(update_fields=["status", "updated_at"])
        messages.success(request, f"Order #{order.pk} marked as served.")
    return redirect("waiter:table_detail", table_id=order.table_id)


@waiter_required
@require_POST
def add_items(request, table_id):
    """Waiter adds items on behalf of the customer sitting at the table."""
    restaurant = request.user.restaurant
    table = get_object_or_404(Table, pk=table_id, restaurant=restaurant)
    active_session = TableSession.objects.filter(table=table, is_active=True).first()

    try:
        cart = json.loads(request.POST.get("cart", "[]"))
    except json.JSONDecodeError:
        cart = []

    if not cart:
        messages.warning(request, "No items selected.")
        return redirect("waiter:table_detail", table_id=table_id)

    # If table is vacant, create a session now using waiter-supplied details
    if not active_session:
        name = request.POST.get("customer_name", "").strip() or "Walk-in"
        phone = request.POST.get("customer_phone", "").strip() or "—"
        active_session = TableSession.objects.create(
            table=table,
            customer_name=name,
            customer_phone=phone,
        )

    order = Order.objects.create(
        restaurant=restaurant,
        table=table,
        table_session=active_session,
        customer_name=active_session.customer_name,
        special_instructions=request.POST.get("special_instructions", "").strip(),
    )

    added = 0
    for entry in cart:
        try:
            item = MenuItem.objects.get(pk=entry["id"], restaurant=restaurant, is_available=True)
            qty = max(1, int(entry.get("qty", 1)))
            OrderItem.objects.create(
                order=order,
                menu_item=item,
                quantity=qty,
                unit_price=item.price,
            )
            added += 1
        except (MenuItem.DoesNotExist, KeyError, ValueError, TypeError):
            pass

    if added:
        order.calculate_total()
        messages.success(request, f"Added {added} item(s) to order #{order.pk}.")
    else:
        order.delete()
        messages.error(request, "Could not add items — they may be unavailable.")

    return redirect("waiter:table_detail", table_id=table_id)
