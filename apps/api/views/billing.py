from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from apps.api.permissions import IsRestaurantAdmin
from apps.api.serializers import InvoiceSerializer, SubscriptionPlanSerializer, SubscriptionSerializer
from apps.billing.models import Invoice, Subscription, SubscriptionPlan


@api_view(["GET"])
@permission_classes([IsRestaurantAdmin])
def billing_dashboard(request):
    restaurant = request.user.restaurant
    sub = getattr(restaurant, "subscription", None)

    # Auto-expire
    if sub and sub.expires_at and timezone.now() > sub.expires_at:
        if sub.status in (Subscription.TRIAL, Subscription.ACTIVE):
            sub.status = Subscription.EXPIRED
            sub.save(update_fields=["status"])

    invoices = Invoice.objects.filter(
        subscription__restaurant=restaurant
    ).order_by("-issued_at")[:10]

    return Response(
        {
            "subscription": SubscriptionSerializer(sub).data if sub else None,
            "plans": SubscriptionPlanSerializer(
                SubscriptionPlan.objects.filter(is_active=True), many=True
            ).data,
            "invoices": InvoiceSerializer(invoices, many=True, context={"request": request}).data,
        }
    )


@api_view(["POST"])
@permission_classes([IsRestaurantAdmin])
def change_plan(request, plan_id):
    restaurant = request.user.restaurant
    try:
        plan = SubscriptionPlan.objects.get(pk=plan_id, is_active=True)
    except SubscriptionPlan.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    sub = getattr(restaurant, "subscription", None)
    if not sub:
        return Response({"detail": "No subscription found."}, status=status.HTTP_400_BAD_REQUEST)

    sub.plan = plan
    sub.status = Subscription.ACTIVE
    now = timezone.now()
    # Advance one month
    try:
        sub.expires_at = now.replace(month=now.month % 12 + 1)
    except ValueError:
        sub.expires_at = now.replace(year=now.year + 1, month=1)
    sub.save()

    Invoice.objects.create(subscription=sub, amount=plan.price_monthly)
    return Response(SubscriptionSerializer(sub).data)
