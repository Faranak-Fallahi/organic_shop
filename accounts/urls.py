from . import views
from .views import CustomerViewSet
from django.urls import path
from rest_framework.routers import DefaultRouter

app_name = "accounts"

router = DefaultRouter()
router.register('customers', CustomerViewSet, basename='customers')

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('logout/', views.UserLogoutView.as_view(), name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('my-comments/', views.my_comments_view, name='my_comments'),
    path('password-change/', views.CustomPasswordChangeView.as_view(), name='password_change'),
    path('password-reset/', views.PhonePasswordResetRequestView.as_view(), name='password_reset_request'),
    path('password-reset/verify/', views.OTPVerifyView.as_view(), name='password_reset_verify'),
    path('password-reset/confirm/', views.SetNewPasswordView.as_view(), name='password_reset_confirm'),
    path('auth/', views.PhoneAuthRequestView.as_view(), name='auth_request'),
    path('auth/verify/', views.PhoneAuthVerifyView.as_view(), name='auth_verify'),

]

urlpatterns += router.urls
