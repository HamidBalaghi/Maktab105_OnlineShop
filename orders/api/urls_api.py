from django.urls import path
from .views_api import AddToOrderItem

urlpatterns = [
    path('add-to-order-item/', AddToOrderItem.as_view(), name='api-add-to-order-item'),
]
