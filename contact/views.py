from django.shortcuts import render
from .models import Branch
from .models import AboutPage


def contact_us_view(request):
    branches = Branch.objects.filter(is_active=True)
    return render(request, "contact/contact_us.html", {"branches": branches})

def about_us_view(request):
    about_page = AboutPage.objects.prefetch_related(
        "features",
        "categories"
    ).first()

    return render(
        request,
        "contact/about_us.html",
        {
            "about_page": about_page,
        }
    )