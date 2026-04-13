from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta

from .forms import RestaurantRegistrationForm
from .models import User


def landing(request):
    if request.user.is_authenticated:
        return redirect("dashboard:home")
    return render(request, "landing.html")


def register(request):
    if request.user.is_authenticated:
        return redirect("dashboard:home")
    if request.method == "POST":
        form = RestaurantRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create restaurant and trial subscription
            _setup_restaurant(user, form)
            login(request, user)
            messages.success(request, "Welcome! Your 14-day free trial has started.")
            return redirect("dashboard:home")
    else:
        form = RestaurantRegistrationForm()
    return render(request, "accounts/register.html", {"form": form})


def _setup_restaurant(user, form):
    from apps.tenants.models import Restaurant
    from apps.billing.models import SubscriptionPlan, Subscription

    restaurant = Restaurant.objects.create(
        name=form.cleaned_data["restaurant_name"],
        owner=user,
        phone=form.cleaned_data.get("phone", ""),
        city=form.cleaned_data.get("city", ""),
    )
    user.restaurant = restaurant
    user.save(update_fields=["restaurant"])

    # Auto-assign 14-day Pro trial
    pro_plan = SubscriptionPlan.objects.filter(name="Pro").first()
    if pro_plan:
        Subscription.objects.create(
            restaurant=restaurant,
            plan=pro_plan,
            status=Subscription.TRIAL,
            expires_at=timezone.now() + timedelta(days=14),
        )


def _home_for_user(user):
    """Return the correct landing URL after login based on role."""
    if user.role == User.KITCHEN_STAFF:
        return "kitchen:board"
    if user.role == User.WAITER:
        return "waiter:tables"
    return "dashboard:home"


def user_login(request):
    if request.user.is_authenticated:
        return redirect(_home_for_user(request.user))
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            # Honour ?next= (set by @login_required), otherwise send to role home
            next_url = request.GET.get("next") or _home_for_user(user)
            return redirect(next_url)
        messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, "accounts/login.html", {"form": form})


def user_logout(request):
    logout(request)
    return redirect("accounts:login")
