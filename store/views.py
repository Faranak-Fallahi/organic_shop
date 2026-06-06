from django.shortcuts import render, get_object_or_404
from . import models


def product_list(request):
    products = models.Product.objects.filter(is_active=True)
    categories = models.Category.objects.all()
    

    context = {
        "products": products,
        "categories": categories,
        
    }

    return render(request, "store/product_list.html", context)

