from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    SUPER_ADMIN = "super_admin"
    RESTAURANT_ADMIN = "restaurant_admin"
    KITCHEN_STAFF = "kitchen_staff"
    WAITER = "waiter"

    ROLE_CHOICES = [
        (SUPER_ADMIN, "Super Admin"),
        (RESTAURANT_ADMIN, "Restaurant Admin"),
        (KITCHEN_STAFF, "Kitchen Staff"),
        (WAITER, "Waiter"),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=RESTAURANT_ADMIN)
    restaurant = models.ForeignKey(
        "tenants.Restaurant",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="staff",
    )

    def is_restaurant_admin(self):
        return self.role == self.RESTAURANT_ADMIN

    def is_kitchen_staff(self):
        return self.role == self.KITCHEN_STAFF

    def is_super_admin(self):
        return self.role == self.SUPER_ADMIN
