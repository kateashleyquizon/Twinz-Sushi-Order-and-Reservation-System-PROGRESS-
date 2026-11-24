
from django.urls import path
from . import views

urlpatterns = [
    path('', views.welcome, name='welcome'),
    path('login/', views.employee_login, name='login'),
    path('logout/', views.employee_logout, name='logout'),

    path('dashboard/', views.dashboard, name='dashboard'),

    # In-store orders
    path('orders/', views.order_list, name='orders'),
    path('orders/add/', views.add_order, name='add_order'),
    path(
        'orders/<int:order_id>/update/',
        views.update_order,
        name='update_order'
    ),

    # Incoming reservations
    path('reservations/', views.reservation_list, name='reservations'),
    path(
        'reservations/<int:reservation_id>/edit/',
        views.edit_reservation,
        name='edit_reservation'
    ),
    path(
        'reservations/<int:reservation_id>/update/',
        views.update_reservation,
        name='update_reservation'
    ),

    # Reserved order monitoring
    path(
        'reserved-orders/',
        views.reservation_orders,
        name='reservation_orders'
    ),

    # Transactions
    path(
        'transactions/',
        views.transaction_list,
        name='transactions'
    ),
]
