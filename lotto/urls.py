from django.urls import path
from . import views

urlpatterns = [
    path("buy/", views.buy_ticket, name="buy_ticket"),
    path("buy/done/<int:ticket_id>/", views.buy_ticket_done, name="buy_ticket_done"),
]
