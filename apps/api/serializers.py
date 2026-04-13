from rest_framework import serializers
from apps.accounts.models import User
from apps.tenants.models import Restaurant
from apps.billing.models import SubscriptionPlan, Subscription, Invoice
from apps.menu.models import MenuCategory, MenuItem
from apps.tables.models import Table
from apps.orders.models import Order, OrderItem, TableSession


# ── Auth / User ───────────────────────────────────────────────────────────────

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name", "role", "restaurant"]


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(min_length=8, write_only=True)
    restaurant_name = serializers.CharField(max_length=200)
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    city = serializers.CharField(max_length=100, required=False, allow_blank=True)

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already taken.")
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already registered.")
        return value


# ── Restaurant ────────────────────────────────────────────────────────────────

class RestaurantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = [
            "id", "name", "slug", "logo", "address",
            "phone", "city", "state", "currency", "is_active",
        ]
        read_only_fields = ["slug"]


# ── Billing ───────────────────────────────────────────────────────────────────

class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = [
            "id", "name", "price_monthly", "max_tables",
            "max_menu_items", "has_analytics", "display_order",
        ]


class SubscriptionSerializer(serializers.ModelSerializer):
    plan = SubscriptionPlanSerializer(read_only=True)

    class Meta:
        model = Subscription
        fields = ["id", "plan", "status", "starts_at", "expires_at"]


class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = ["id", "amount", "status", "issued_at", "paid_at", "pdf_file"]


# ── Menu ──────────────────────────────────────────────────────────────────────

class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = [
            "id", "category", "name", "description", "price",
            "image", "is_veg", "is_available", "display_order",
        ]
        read_only_fields = ["id"]

    def validate_category(self, value):
        request = self.context.get("request")
        if request and value.restaurant != request.user.restaurant:
            raise serializers.ValidationError("Category does not belong to your restaurant.")
        return value


class MenuItemReadSerializer(serializers.ModelSerializer):
    """Used for nested reads (includes category name)."""
    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = MenuItem
        fields = [
            "id", "category", "category_name", "name", "description",
            "price", "image", "is_veg", "is_available", "display_order",
        ]


class MenuCategorySerializer(serializers.ModelSerializer):
    items = MenuItemReadSerializer(many=True, read_only=True)

    class Meta:
        model = MenuCategory
        fields = ["id", "name", "display_order", "is_active", "items"]
        read_only_fields = ["id"]


# ── Tables ────────────────────────────────────────────────────────────────────

class TableSerializer(serializers.ModelSerializer):
    qr_image_url = serializers.SerializerMethodField()

    class Meta:
        model = Table
        fields = ["id", "name", "qr_token", "qr_image", "qr_image_url", "is_active"]
        read_only_fields = ["id", "qr_token", "qr_image", "qr_image_url"]

    def get_qr_image_url(self, obj):
        request = self.context.get("request")
        if obj.qr_image and request:
            return request.build_absolute_uri(obj.qr_image.url)
        return None


# ── Orders ────────────────────────────────────────────────────────────────────

class OrderItemSerializer(serializers.ModelSerializer):
    menu_item_name = serializers.CharField(source="menu_item.name", read_only=True)

    class Meta:
        model = OrderItem
        fields = ["id", "menu_item", "menu_item_name", "quantity", "unit_price", "notes"]


class TableSessionSerializer(serializers.ModelSerializer):
    running_total = serializers.SerializerMethodField()

    class Meta:
        model = TableSession
        fields = [
            "id", "table", "customer_name", "customer_phone",
            "is_active", "created_at", "running_total",
        ]

    def get_running_total(self, obj):
        return str(obj.running_total())


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    table_name = serializers.CharField(source="table.name", read_only=True)
    session_phone = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            "id", "table", "table_name", "table_session", "status",
            "payment_method", "payment_status", "paid_at",
            "customer_name", "special_instructions", "total_amount",
            "created_at", "updated_at", "items", "session_phone",
        ]

    def get_session_phone(self, obj):
        if obj.table_session:
            return obj.table_session.customer_phone
        return ""


# ── Customer (public) ─────────────────────────────────────────────────────────

class CustomerMenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ["id", "name", "description", "price", "image", "is_veg", "is_available"]


class CustomerMenuCategorySerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField()

    class Meta:
        model = MenuCategory
        fields = ["id", "name", "display_order", "items"]

    def get_items(self, obj):
        available = obj.items.filter(is_available=True)
        return CustomerMenuItemSerializer(available, many=True, context=self.context).data


class CustomerSessionSerializer(serializers.ModelSerializer):
    orders = OrderSerializer(many=True, read_only=True)
    running_total = serializers.SerializerMethodField()

    class Meta:
        model = TableSession
        fields = [
            "id", "customer_name", "customer_phone",
            "created_at", "running_total", "orders",
        ]

    def get_running_total(self, obj):
        return str(obj.running_total())
