from django.urls import path
from . import views

app_name = 'orders'


urlpatterns = [
    path('add-product/', views.AddToOrderItem.as_view(), name='add-product'),
    path('cart/', views.CartView.as_view(), name='cart'),
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    path('paid-orders/', views.PaidOrdersView.as_view(), name='paid-orders'),
    path('order/<int:pk>/', views.OrderDetailsView.as_view(), name='order-details'),
]
