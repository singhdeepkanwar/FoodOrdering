from django.urls import path
from . import customer_views

urlpatterns = [
    path("<uuid:qr_token>/", customer_views.ordering_page, name="customer_menu"),
    path("<uuid:qr_token>/checkin/", customer_views.checkin, name="customer_checkin"),
    path("<uuid:qr_token>/order/", customer_views.place_order, name="customer_place_order"),
    path("<uuid:qr_token>/confirmation/<int:order_id>/", customer_views.order_confirmation, name="customer_confirmation"),
    path("<uuid:qr_token>/track/<int:order_id>/", customer_views.order_track, name="customer_track"),
]
