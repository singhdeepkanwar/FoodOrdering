from datetime import timedelta

from django.db import transaction
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import User
from apps.api.serializers import RegisterSerializer, UserSerializer


@api_view(["POST"])
@permission_classes([AllowAny])
@transaction.atomic
def register(request):
    serializer = RegisterSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    data = serializer.validated_data
    user = User.objects.create_user(
        username=data["username"],
        email=data["email"],
        password=data["password"],
        role=User.RESTAURANT_ADMIN,
    )
    _setup_restaurant(user, data)

    refresh = RefreshToken.for_user(user)
    return Response(
        {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": UserSerializer(user).data,
        },
        status=status.HTTP_201_CREATED,
    )


def _setup_restaurant(user, data):
    from apps.tenants.models import Restaurant
    from apps.billing.models import SubscriptionPlan, Subscription

    restaurant = Restaurant.objects.create(
        name=data["restaurant_name"],
        owner=user,
        phone=data.get("phone", ""),
        city=data.get("city", ""),
    )
    user.restaurant = restaurant
    user.save(update_fields=["restaurant"])

    pro_plan = SubscriptionPlan.objects.filter(name="Pro").first()
    if pro_plan:
        Subscription.objects.create(
            restaurant=restaurant,
            plan=pro_plan,
            status=Subscription.TRIAL,
            expires_at=timezone.now() + timedelta(days=14),
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me(request):
    return Response(UserSerializer(request.user).data)
