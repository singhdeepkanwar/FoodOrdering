from django.db import models


class MenuCategory(models.Model):
    restaurant = models.ForeignKey(
        "tenants.Restaurant", on_delete=models.CASCADE, related_name="categories"
    )
    name = models.CharField(max_length=100)
    display_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.restaurant.name} — {self.name}"

    class Meta:
        ordering = ["display_order", "name"]
        verbose_name_plural = "menu categories"


class MenuItem(models.Model):
    restaurant = models.ForeignKey(
        "tenants.Restaurant", on_delete=models.CASCADE, related_name="menu_items"
    )
    category = models.ForeignKey(
        MenuCategory, on_delete=models.CASCADE, related_name="items"
    )
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    image = models.ImageField(upload_to="menu_items/", null=True, blank=True)
    is_veg = models.BooleanField(default=True)
    is_available = models.BooleanField(default=True)
    display_order = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.name} (₹{self.price})"

    class Meta:
        ordering = ["display_order", "name"]
