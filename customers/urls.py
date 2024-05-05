from django.urls import path
from . import views

app_name = 'customers'

urlpatterns = [
    path('edit-profile/', views.EditProfileView.as_view(), name='edit-profile'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('change-password/', views.CustomPasswordChangeView.as_view(), name='change-password'),
    path('new-address/', views.AddNewAddressView.as_view(), name='new-address'),
]
