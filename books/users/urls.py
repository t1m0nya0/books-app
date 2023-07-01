from django.urls import path
from .views import RegistrationView, LoginView, LogoutView,ChangePasswordView
from rest_framework_simplejwt import views as jwt_views

app_name = 'users'

urlpatterns = [
    path('accounts/register', RegistrationView.as_view()),
    path('accounts/login', LoginView.as_view()),
    path('accounts/logout', LogoutView.as_view()),
    path('accounts/change-password', ChangePasswordView.as_view()),
]
