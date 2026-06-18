from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView 
from django.contrib.auth import views as auth_views
app_name = "accounts"



urlpatterns = [
    path('register/', views.register, name='register'),
    path("login/", views.UserLoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("profile/", views.profile_view, name="profile"),
    path('password-change/',views.CustomPasswordChangeView.as_view(), name='password_change'),
     path('password-reset/', views.PhonePasswordResetRequestView.as_view(), name='password_reset_request'),
    path('password-reset/verify/', views.OTPVerifyView.as_view(), name='password_reset_verify'),
    path('password-reset/confirm/', views.SetNewPasswordView.as_view(), name='password_reset_confirm'),
    
    
   


]
