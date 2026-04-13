from django.urls import path
from . import views

app_name = "kitchen"

urlpatterns = [
    path("", views.kitchen_board, name="board"),
    path("orders/", views.orders_partial, name="orders_partial"),
    path("orders/<int:order_id>/advance/", views.update_order_status, name="advance_order"),
    path("orders/<int:order_id>/cancel/", views.cancel_order, name="cancel_order"),
]
