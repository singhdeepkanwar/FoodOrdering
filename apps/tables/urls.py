from django.urls import path
from . import views

app_name = "tables"

urlpatterns = [
    path("", views.table_list, name="list"),
    path("add/", views.table_create, name="create"),
    path("<int:pk>/edit/", views.table_edit, name="edit"),
    path("<int:pk>/delete/", views.table_delete, name="delete"),
    path("<int:pk>/qr/", views.table_qr_download, name="qr_download"),
]
