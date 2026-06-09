from django.urls import path
from . import views
from .views import UserLoginView , profile_view
from django.contrib.auth.views import LogoutView 
urlpatterns = [
    path('register/', views.register, name='register'),
    path("login/", UserLoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
   path("profile/", profile_view, name="profile"),
]
