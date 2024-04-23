from django.urls import path
from . import views

app_name = 'products'


urlpatterns = [
    path('products/<slug:slug>/<int:pk>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('', views.HomePageView.as_view(), name='home'),
]
