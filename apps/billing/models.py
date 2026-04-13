from django.db import models
from django.utils import timezone
from datetime import timedelta


class SubscriptionPlan(models.Model):
    name = models.CharField(max_length=50)  # Free / Starter / Pro
    price_monthly = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    max_tables = models.IntegerField(default=2)       # -1 = unlimited
    max_menu_items = models.IntegerField(default=20)  # -1 = unlimited
    has_analytics = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    display_order = models.IntegerField(default=0)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["display_order"]


class Subscription(models.Model):
    TRIAL = "trial"
    ACTIVE = "active"
    EXPIRED = "expired"
    CANCELLED = "cancelled"

    STATUS_CHOICES = [
        (TRIAL, "Trial"),
        (ACTIVE, "Active"),
        (EXPIRED, "Expired"),
        (CANCELLED, "Cancelled"),
    ]

    restaurant = models.OneToOneField(
        "tenants.Restaurant", on_delete=models.CASCADE, related_name="subscription"
    )
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.PROTECT)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default=TRIAL)
    starts_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField(null=True, blank=True)

    def is_valid(self):
        if self.status in (self.TRIAL, self.ACTIVE):
            if self.expires_at and timezone.now() > self.expires_at:
                return False
            return True
        return False

    def __str__(self):
        return f"{self.restaurant.name} — {self.plan.name} ({self.status})"


class Invoice(models.Model):
    UNPAID = "unpaid"
    PAID = "paid"

    STATUS_CHOICES = [
        (UNPAID, "Unpaid"),
        (PAID, "Paid"),
    ]

    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, related_name="invoices")
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=UNPAID)
    issued_at = models.DateTimeField(default=timezone.now)
    paid_at = models.DateTimeField(null=True, blank=True)
    pdf_file = models.FileField(upload_to="invoices/", null=True, blank=True)
    # Ready for payment gateway integration
    gateway_payment_id = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"Invoice #{self.pk} — {self.subscription.restaurant.name}"
