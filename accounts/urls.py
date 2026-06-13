from django.urls import path
from . import views
from .views import UserLoginView , profile_view , CustomPasswordChangeView
from django.contrib.auth.views import LogoutView 
from django.contrib.auth import views as auth_views
app_name = "accounts"



urlpatterns = [
    path('register/', views.register, name='register'),
    path("login/", UserLoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("profile/", profile_view, name="profile"),
    path(
    'password-change/',
    CustomPasswordChangeView.as_view(),
    name='password_change'),


]
