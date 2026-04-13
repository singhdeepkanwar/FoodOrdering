from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse

from .models import Table
from .forms import TableForm


def _check_table_limit(restaurant):
    subscription = restaurant.active_subscription
    if not subscription:
        return False
    limit = subscription.plan.max_tables
    if limit == -1:
        return True
    return restaurant.tables.count() < limit


@login_required
def table_list(request):
    restaurant = request.user.restaurant
    tables = Table.objects.filter(restaurant=restaurant)
    return render(request, "dashboard/tables/list.html", {"tables": tables})


@login_required
def table_create(request):
    restaurant = request.user.restaurant
    if not _check_table_limit(restaurant):
        messages.error(request, "You've reached your plan's table limit. Please upgrade.")
        return redirect("tables:list")
    if request.method == "POST":
        form = TableForm(request.POST)
        if form.is_valid():
            table = form.save(commit=False)
            table.restaurant = restaurant
            table.save()
            # Generate QR code
            base_url = request.build_absolute_uri("/").rstrip("/")
            table.generate_qr(base_url)
            table.save()
            messages.success(request, f"Table '{table.name}' created with QR code.")
            return redirect("tables:list")
    else:
        form = TableForm()
    return render(request, "dashboard/tables/form.html", {"form": form, "action": "Add"})


@login_required
def table_edit(request, pk):
    restaurant = request.user.restaurant
    table = get_object_or_404(Table, pk=pk, restaurant=restaurant)
    if request.method == "POST":
        form = TableForm(request.POST, instance=table)
        if form.is_valid():
            form.save()
            messages.success(request, "Table updated.")
            return redirect("tables:list")
    else:
        form = TableForm(instance=table)
    return render(request, "dashboard/tables/form.html", {"form": form, "action": "Edit", "table": table})


@login_required
def table_delete(request, pk):
    restaurant = request.user.restaurant
    table = get_object_or_404(Table, pk=pk, restaurant=restaurant)
    if request.method == "POST":
        table.delete()
        messages.success(request, "Table deleted.")
    return redirect("tables:list")


@login_required
def table_qr_download(request, pk):
    restaurant = request.user.restaurant
    table = get_object_or_404(Table, pk=pk, restaurant=restaurant)
    if not table.qr_image:
        base_url = request.build_absolute_uri("/").rstrip("/")
        table.generate_qr(base_url)
        table.save()
    with open(table.qr_image.path, "rb") as f:
        response = HttpResponse(f.read(), content_type="image/png")
        response["Content-Disposition"] = f'attachment; filename="qr_{table.name}.png"'
        return response
