from django.db import models


class TableSession(models.Model):
    """
    Represents a single customer sitting at a table.
    Created at check-in, deactivated when the bill is paid.
    Linking orders to a session lets us show the full running bill
    and clear the table cleanly for the next guest.
    """
    table = models.ForeignKey(
        "tables.Table", on_delete=models.CASCADE, related_name="sessions"
    )
    customer_name = models.CharField(max_length=100)
    customer_phone = models.CharField(max_length=15)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer_name} @ {self.table} ({'active' if self.is_active else 'closed'})"

    def running_total(self):
        return sum(o.total_amount for o in self.orders.all())

    class Meta:
        ordering = ["-created_at"]


class Order(models.Model):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PREPARING = "preparing"
    READY = "ready"
    SERVED = "served"
    CANCELLED = "cancelled"

    STATUS_CHOICES = [
        (PENDING, "Pending"),
        (CONFIRMED, "Confirmed"),
        (PREPARING, "Preparing"),
        (READY, "Ready"),
        (SERVED, "Served"),
        (CANCELLED, "Cancelled"),
    ]

    CASH = "cash"
    ONLINE = "online"
    PAYMENT_METHOD_CHOICES = [
        (CASH, "Cash"),
        (ONLINE, "Online"),
    ]

    UNPAID = "unpaid"
    PAID = "paid"
    PAYMENT_STATUS_CHOICES = [
        (UNPAID, "Unpaid"),
        (PAID, "Paid"),
    ]

    restaurant = models.ForeignKey(
        "tenants.Restaurant", on_delete=models.CASCADE, related_name="orders"
    )
    table = models.ForeignKey(
        "tables.Table", on_delete=models.SET_NULL, null=True, related_name="orders"
    )
    table_session = models.ForeignKey(
        TableSession, on_delete=models.SET_NULL, null=True, blank=True, related_name="orders"
    )
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default=PENDING)
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHOD_CHOICES, default=CASH)
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES, default=UNPAID)
    paid_at = models.DateTimeField(null=True, blank=True)
    customer_name = models.CharField(max_length=100, blank=True)
    special_instructions = models.TextField(blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.pk} — {self.table} ({self.status})"

    def calculate_total(self):
        self.total_amount = sum(item.subtotal() for item in self.items.all())
        self.save(update_fields=["total_amount"])

    class Meta:
        ordering = ["-created_at"]


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    menu_item = models.ForeignKey(
        "menu.MenuItem", on_delete=models.PROTECT, related_name="order_items"
    )
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=8, decimal_places=2)  # snapshot at order time
    notes = models.CharField(max_length=200, blank=True)

    def subtotal(self):
        return self.quantity * self.unit_price

    def __str__(self):
        return f"{self.quantity}x {self.menu_item.name}"
