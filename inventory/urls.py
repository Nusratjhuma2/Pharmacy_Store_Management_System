from django.urls import path
from django.contrib.auth.views import LogoutView

from . import views


urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', views.register_view, name='register'),

    path('', views.medicine_list, name='medicine_list'),
    path('medicines/add/', views.medicine_add, name='medicine_add'),
    path('medicines/<int:pk>/edit/', views.medicine_edit, name='medicine_edit'),
    path('medicines/<int:pk>/delete/', views.medicine_delete, name='medicine_delete'),

    path('sell/', views.sell_view, name='sell'),
    path('cart/', views.sell_view, name='cart'),
    path('receipt/<int:pk>/', views.receipt_view, name='receipt'),
    path('sales/', views.sales_history, name='sales_history'),
    path('cart/add/<int:pk>/', views.cart_add, name='cart_add'),
    path('cart/clear/', views.cart_clear, name='cart_clear'),
    path('cart/remove/', views.cart_remove, name='cart_remove'),
]


