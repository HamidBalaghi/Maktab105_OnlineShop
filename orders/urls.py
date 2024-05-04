from django.urls import path
from . import views

app_name = 'orders'


urlpatterns = [
    path('add-product/', views.AddToOrderItem.as_view(), name='add-product'),
]
