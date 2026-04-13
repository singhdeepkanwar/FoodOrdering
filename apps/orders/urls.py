from django.urls import path
from . import views

app_name = "orders"

urlpatterns = [
    path("", views.order_list, name="list"),
    path("<int:order_id>/mark-paid/", views.mark_paid, name="mark_paid"),
]
