from django.urls import path
from . import views

app_name = 'customers'

urlpatterns = [
    path('edit-profile/', views.EditProfileView.as_view(), name='edit-profile'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('change-password/', views.CustomPasswordChangeView.as_view(), name='change-password'),
    path('new-address/', views.AddNewAddressView.as_view(), name='new-address'),
    path('address/', views.ShowAddressView.as_view(), name='address'),
    path('address/<int:pk>/delete/', views.DeleteAddressView.as_view(), name='delete-address'),
]
