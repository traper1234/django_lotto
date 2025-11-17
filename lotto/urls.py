from django.urls import path
from . import views

urlpatterns = [
    # 홈
    path("", views.home, name="home"),
    
    # 인증
    path("signup/", views.signup, name="signup"),
    path("login/", views.user_login, name="login"),
    path("logout/", views.user_logout, name="logout"),
    
    # 사용자 기능
    path("buy/", views.buy_ticket, name="buy_ticket"),
    path("buy/done/<int:ticket_id>/", views.buy_ticket_done, name="buy_ticket_done"),
    path("my-tickets/", views.my_tickets, name="my_tickets"),
    
    # 관리자 기능
    path("admin/sales/", views.admin_sales, name="admin_sales"),
    path("admin/draw/", views.admin_draw, name="admin_draw"),
    path("admin/winners/", views.admin_winners, name="admin_winners"),
]
