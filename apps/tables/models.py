import io
import uuid
import qrcode
from django.db import models
from django.core.files import File


class Table(models.Model):
    restaurant = models.ForeignKey(
        "tenants.Restaurant", on_delete=models.CASCADE, related_name="tables"
    )
    name = models.CharField(max_length=50)  # e.g. "Table 1", "Rooftop 3"
    qr_token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    qr_image = models.ImageField(upload_to="qr_codes/", blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.restaurant.name} — {self.name}"

    def generate_qr(self, base_url):
        url = f"{base_url}/t/{self.qr_token}/"
        img = qrcode.make(url)
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        filename = f"qr_{self.qr_token}.png"
        self.qr_image.save(filename, File(buffer), save=False)

    class Meta:
        ordering = ["name"]
