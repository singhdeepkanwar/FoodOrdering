from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse

from .models import MenuCategory, MenuItem
from .forms import CategoryForm, MenuItemForm


def _check_limit(restaurant, model_class, plan_limit_field):
    subscription = restaurant.active_subscription
    if not subscription:
        return False
    limit = getattr(subscription.plan, plan_limit_field)
    if limit == -1:
        return True  # unlimited
    current = model_class.objects.filter(restaurant=restaurant).count()
    return current < limit


@login_required
def menu_list(request):
    restaurant = request.user.restaurant
    categories = MenuCategory.objects.filter(restaurant=restaurant).prefetch_related("items")
    return render(request, "dashboard/menu/list.html", {"categories": categories, "restaurant": restaurant})


@login_required
def category_create(request):
    restaurant = request.user.restaurant
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            cat = form.save(commit=False)
            cat.restaurant = restaurant
            cat.save()
            messages.success(request, "Category created.")
            return redirect("menu:list")
    else:
        form = CategoryForm()
    return render(request, "dashboard/menu/category_form.html", {"form": form, "action": "Create"})


@login_required
def category_edit(request, pk):
    restaurant = request.user.restaurant
    category = get_object_or_404(MenuCategory, pk=pk, restaurant=restaurant)
    if request.method == "POST":
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, "Category updated.")
            return redirect("menu:list")
    else:
        form = CategoryForm(instance=category)
    return render(request, "dashboard/menu/category_form.html", {"form": form, "action": "Edit"})


@login_required
def category_delete(request, pk):
    restaurant = request.user.restaurant
    category = get_object_or_404(MenuCategory, pk=pk, restaurant=restaurant)
    if request.method == "POST":
        category.delete()
        messages.success(request, "Category deleted.")
    return redirect("menu:list")


@login_required
def item_create(request):
    restaurant = request.user.restaurant
    if not _check_limit(restaurant, MenuItem, "max_menu_items"):
        messages.error(request, "You've reached your plan's menu item limit. Please upgrade.")
        return redirect("menu:list")
    if request.method == "POST":
        form = MenuItemForm(request.POST, request.FILES, restaurant=restaurant)
        if form.is_valid():
            item = form.save(commit=False)
            item.restaurant = restaurant
            item.save()
            messages.success(request, "Menu item added.")
            return redirect("menu:list")
    else:
        form = MenuItemForm(restaurant=restaurant)
    return render(request, "dashboard/menu/item_form.html", {"form": form, "action": "Add"})


@login_required
def item_edit(request, pk):
    restaurant = request.user.restaurant
    item = get_object_or_404(MenuItem, pk=pk, restaurant=restaurant)
    if request.method == "POST":
        form = MenuItemForm(request.POST, request.FILES, instance=item, restaurant=restaurant)
        if form.is_valid():
            form.save()
            messages.success(request, "Menu item updated.")
            return redirect("menu:list")
    else:
        form = MenuItemForm(instance=item, restaurant=restaurant)
    return render(request, "dashboard/menu/item_form.html", {"form": form, "action": "Edit"})


@login_required
def item_delete(request, pk):
    restaurant = request.user.restaurant
    item = get_object_or_404(MenuItem, pk=pk, restaurant=restaurant)
    if request.method == "POST":
        item.delete()
        messages.success(request, "Menu item deleted.")
    return redirect("menu:list")


@login_required
def item_toggle_availability(request, pk):
    restaurant = request.user.restaurant
    item = get_object_or_404(MenuItem, pk=pk, restaurant=restaurant)
    item.is_available = not item.is_available
    item.save(update_fields=["is_available"])
    return JsonResponse({"is_available": item.is_available})
