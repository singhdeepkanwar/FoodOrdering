from django.urls import path
from . import views

app_name = "billing"

urlpatterns = [
    path("", views.billing_dashboard, name="dashboard"),
    path("plan/<int:plan_id>/change/", views.change_plan, name="change_plan"),
]
