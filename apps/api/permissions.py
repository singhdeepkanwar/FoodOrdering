from rest_framework.permissions import BasePermission


class IsRestaurantAdmin(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role in ("restaurant_admin",)
            and request.user.restaurant is not None
        )


class IsKitchenOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role in ("restaurant_admin", "kitchen_staff")
            and request.user.restaurant is not None
        )


class IsWaiterOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role in ("restaurant_admin", "waiter")
            and request.user.restaurant is not None
        )


class IsRestaurantStaff(BasePermission):
    """Any role that belongs to a restaurant."""
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.restaurant is not None
        )
