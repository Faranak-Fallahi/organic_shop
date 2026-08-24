from django.urls import path
from . import views

app_name = "contact"

urlpatterns = [
    path("", views.contact_us_view, name="contact-us"),
    path("about-us/", views.about_us_view, name="about-us"),
]
