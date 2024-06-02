from django.urls import path
from . import views_api
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('add-to-order-item/', views_api.AddToOrderItem.as_view(), name='api-add-to-order-item'),
    path('cart/', views_api.CartView.as_view(), name='api-cart'),
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),
    path('checkout/', views_api.CheckoutView.as_view(), name='api-checkout'),
    path('paid-orders/', views_api.PaidOrdersView.as_view(), name='api-paid-orders'),
    path('order/<int:pk>/', views_api.OrderDetailView.as_view(), name='api-order-details'),
]
