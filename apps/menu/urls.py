from django.urls import path
from . import views

app_name = "menu"

urlpatterns = [
    path("", views.menu_list, name="list"),
    path("categories/add/", views.category_create, name="category_create"),
    path("categories/<int:pk>/edit/", views.category_edit, name="category_edit"),
    path("categories/<int:pk>/delete/", views.category_delete, name="category_delete"),
    path("items/add/", views.item_create, name="item_create"),
    path("items/<int:pk>/edit/", views.item_edit, name="item_edit"),
    path("items/<int:pk>/delete/", views.item_delete, name="item_delete"),
    path("items/<int:pk>/toggle/", views.item_toggle_availability, name="item_toggle"),
]
