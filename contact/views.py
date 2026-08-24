from django.shortcuts import render
from .models import Branch


def contact_us_view(request):
    branches = Branch.objects.filter(is_active=True)
    return render(request, "contact/contact_us.html", {"branches": branches})

def about_us_view(request):
    return render(request, "contact/about_us.html")
