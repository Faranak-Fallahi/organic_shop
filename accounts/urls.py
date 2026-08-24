from . import views
from .views import CustomerViewSet
from django.contrib.auth.views import LogoutView
from django.urls import path
from rest_framework.routers import DefaultRouter

app_name = "accounts"

router = DefaultRouter()
router.register('customers', CustomerViewSet, basename='customers')

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('password-change/', views.CustomPasswordChangeView.as_view(), name='password_change'),
    path('password-reset/', views.PhonePasswordResetRequestView.as_view(), name='password_reset_request'),
    path('password-reset/verify/', views.OTPVerifyView.as_view(), name='password_reset_verify'),
    path('password-reset/confirm/', views.SetNewPasswordView.as_view(), name='password_reset_confirm'),
    path('auth/', views.PhoneAuthRequestView.as_view(), name='auth_request'),
    path('auth/verify/', views.PhoneAuthVerifyView.as_view(), name='auth_verify'),

]

urlpatterns += router.urls
