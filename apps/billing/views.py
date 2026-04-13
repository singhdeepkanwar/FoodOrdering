from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

from .models import SubscriptionPlan, Subscription, Invoice


@login_required
def billing_dashboard(request):
    restaurant = request.user.restaurant
    subscription = getattr(restaurant, "subscription", None)
    plans = SubscriptionPlan.objects.filter(is_active=True)
    invoices = Invoice.objects.filter(subscription__restaurant=restaurant).order_by("-issued_at")[:10]

    # Check if subscription expired and update status
    if subscription and subscription.expires_at and timezone.now() > subscription.expires_at:
        if subscription.status in (Subscription.TRIAL, Subscription.ACTIVE):
            subscription.status = Subscription.EXPIRED
            subscription.save(update_fields=["status"])

    return render(request, "dashboard/billing/dashboard.html", {
        "subscription": subscription,
        "plans": plans,
        "invoices": invoices,
    })


@login_required
def change_plan(request, plan_id):
    restaurant = request.user.restaurant
    plan = get_object_or_404(SubscriptionPlan, pk=plan_id, is_active=True)
    subscription = getattr(restaurant, "subscription", None)

    if request.method == "POST":
        if subscription:
            subscription.plan = plan
            subscription.status = Subscription.ACTIVE
            subscription.expires_at = timezone.now().replace(
                month=timezone.now().month % 12 + 1
            ) if timezone.now().month < 12 else timezone.now().replace(
                year=timezone.now().year + 1, month=1
            )
            subscription.save()
            # Create invoice
            Invoice.objects.create(
                subscription=subscription,
                amount=plan.price_monthly,
            )
            messages.success(request, f"Plan changed to {plan.name}. Invoice created.")
        else:
            messages.error(request, "No subscription found.")
        return redirect("billing:dashboard")

    return render(request, "dashboard/billing/confirm_plan.html", {"plan": plan, "subscription": subscription})
