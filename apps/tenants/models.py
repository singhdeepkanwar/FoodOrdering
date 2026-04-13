from django.db import models
from django.utils.text import slugify


class Restaurant(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    owner = models.OneToOneField(
        "accounts.User", on_delete=models.CASCADE, related_name="owned_restaurant"
    )
    logo = models.ImageField(upload_to="logos/", null=True, blank=True)
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    currency = models.CharField(max_length=5, default="INR")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name) or "restaurant"
            slug = base
            n = 1
            while Restaurant.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                n += 1
                slug = f"{base}-{n}"
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    @property
    def active_subscription(self):
        try:
            return self.subscription
        except Exception:
            return None
