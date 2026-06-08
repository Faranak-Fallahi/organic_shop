from django.urls import path
from . import views
from .views import UserLoginView

urlpatterns = [
    path('register/', views.register, name='register'),
    path("login/", UserLoginView.as_view(), name="login"),
]
