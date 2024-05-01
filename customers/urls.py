from django.urls import path
from . import views

app_name = 'customers'

urlpatterns = [
    path('edit-profile/', views.EditProfileView.as_view(), name='edit-profile'),
]
