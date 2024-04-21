from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('signup/', views.SignupView.as_view(), name='signup'),
    path('login/', views.CustomUserLoginView.as_view(), name='login'),
    path('activation/<int:pk>', views.UserActivationView.as_view(), name='activation'),
]
