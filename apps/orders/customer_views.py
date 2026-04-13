import json
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST

from apps.tables.models import Table
from apps.menu.models import MenuCategory, MenuItem
from .models import Order, OrderItem, TableSession


SESSION_KEY = "ts_{}"   # Django session key per table: ts_<qr_token>


def _get_active_session(request, qr_token):
    """Return the active TableSession for this browser+table, or None."""
    ts_pk = request.session.get(SESSION_KEY.format(qr_token))
    if not ts_pk:
        return None
    try:
        ts = TableSession.objects.get(pk=ts_pk, is_active=True)
        return ts
    except TableSession.DoesNotExist:
        # Session was cleared (bill paid) — remove stale cookie reference
        request.session.pop(SESSION_KEY.format(qr_token), None)
        return None


def ordering_page(request, qr_token):
    table = get_object_or_404(Table, qr_token=qr_token, is_active=True)
    restaurant = table.restaurant

    if not restaurant.is_active:
        return render(request, "customer/closed.html", {"restaurant": restaurant})

    ts = _get_active_session(request, qr_token)
    if not ts:
        return redirect("customer_checkin", qr_token=qr_token)

    categories = MenuCategory.objects.filter(
        restaurant=restaurant, is_active=True
    ).prefetch_related("items")

    # All orders for this sitting so customer can see running bill
    session_orders = Order.objects.filter(
        table_session=ts
    ).prefetch_related("items__menu_item").order_by("created_at")

    return render(request, "customer/menu.html", {
        "table": table,
        "restaurant": restaurant,
        "categories": categories,
        "ts": ts,
        "session_orders": session_orders,
    })


def checkin(request, qr_token):
    table = get_object_or_404(Table, qr_token=qr_token, is_active=True)
    restaurant = table.restaurant

    if not restaurant.is_active:
        return render(request, "customer/closed.html", {"restaurant": restaurant})

    # Already checked in?
    ts = _get_active_session(request, qr_token)
    if ts:
        return redirect("customer_menu", qr_token=qr_token)

    error = None
    if request.method == "POST":
        name = request.POST.get("customer_name", "").strip()
        phone = request.POST.get("customer_phone", "").strip()

        if not name or not phone:
            error = "Please enter your name and phone number."
        elif len(phone) < 10:
            error = "Please enter a valid phone number."
        else:
            # Check if this phone already has an active session at this table
            # (e.g. customer switched browser / scanned again on different device)
            existing = TableSession.objects.filter(
                table=table, customer_phone=phone, is_active=True
            ).first()

            if existing:
                ts = existing
            else:
                ts = TableSession.objects.create(
                    table=table,
                    customer_name=name,
                    customer_phone=phone,
                )

            request.session[SESSION_KEY.format(qr_token)] = ts.pk
            request.session.modified = True
            return redirect("customer_menu", qr_token=qr_token)

    return render(request, "customer/checkin.html", {
        "table": table,
        "restaurant": restaurant,
        "error": error,
    })


def place_order(request, qr_token):
    if request.method != "POST":
        return redirect("customer_menu", qr_token=qr_token)

    table = get_object_or_404(Table, qr_token=qr_token, is_active=True)
    restaurant = table.restaurant

    ts = _get_active_session(request, qr_token)
    if not ts:
        return redirect("customer_checkin", qr_token=qr_token)

    try:
        cart = json.loads(request.POST.get("cart", "[]"))
    except json.JSONDecodeError:
        cart = []

    if not cart:
        return redirect("customer_menu", qr_token=qr_token)

    order = Order.objects.create(
        restaurant=restaurant,
        table=table,
        table_session=ts,
        customer_name=ts.customer_name,
        special_instructions=request.POST.get("special_instructions", "").strip(),
    )

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
        except (MenuItem.DoesNotExist, KeyError, ValueError, TypeError):
            pass

    order.calculate_total()
    return redirect("customer_confirmation", qr_token=qr_token, order_id=order.pk)


def order_confirmation(request, qr_token, order_id):
    table = get_object_or_404(Table, qr_token=qr_token)
    order = get_object_or_404(Order, pk=order_id, table=table)
    ts = _get_active_session(request, qr_token)
    session_orders = Order.objects.filter(table_session=ts).prefetch_related("items__menu_item") if ts else [order]
    return render(request, "customer/confirmation.html", {
        "order": order,
        "table": table,
        "ts": ts,
        "session_orders": session_orders,
    })


def order_track(request, qr_token, order_id):
    table = get_object_or_404(Table, qr_token=qr_token)
    order = get_object_or_404(Order, pk=order_id, table=table)
    ts = _get_active_session(request, qr_token)
    if request.headers.get("HX-Request"):
        return render(request, "customer/partials/order_status.html", {"order": order})
    return render(request, "customer/track.html", {"order": order, "table": table, "ts": ts})
