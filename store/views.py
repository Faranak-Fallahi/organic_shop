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

def category_products(request, slug):
    category = get_object_or_404(models.Category, slug=slug)
    products = models.Product.objects.filter(category=category)

   
    sort = request.GET.get("sort")
    if sort == "price_asc":
        products = products.order_by("price")
    elif sort == "price_desc":
        products = products.order_by("-price")
    elif sort == "newest":
        products = products.order_by("-created_at")

    return render(request, "store/category_products.html", {
        "category": category,
        "products": products,
    })
    
    
    