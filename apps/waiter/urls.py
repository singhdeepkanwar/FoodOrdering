from django.urls import path
from . import views

app_name = "waiter"

urlpatterns = [
    path("", views.tables_overview, name="tables"),
    path("table/<int:table_id>/", views.table_detail, name="table_detail"),
    path("table/<int:table_id>/add/", views.add_items, name="add_items"),
    path("order/<int:order_id>/serve/", views.mark_served, name="mark_served"),
]
