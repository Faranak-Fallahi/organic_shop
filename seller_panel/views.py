from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.urls import reverse
from django.db.models import Sum

from store.models import Product, Category
from .forms import SellerProductForm, CategoryForm
from orders.models import Order, OrderItem
from .forms import OrderStatusUpdateForm
from comments.models import ProductComment, PostComment
from django.contrib.auth import get_user_model


@staff_member_required
def dashboard_view(request):
    total_products = Product.objects.count()
    total_categories = Category.objects.count()
    total_orders = Order.objects.count()
    total_users = get_user_model().objects.count()

    paid_orders = Order.objects.filter(status__in=['paid', 'shipped'])

    revenue = 0
    for order in paid_orders.prefetch_related('items'):
        revenue += order.total_price

    bestsellers = (
        OrderItem.objects
        .filter(order__status__in=['paid', 'shipped'])
        .values('product_id', 'product__title', 'product__image')
        .annotate(total_qty=Sum('quantity'))
        .order_by('-total_qty')[:5]
    )

    low_stock_products = (
        Product.objects
        .filter(inventory__lte=5)
        .order_by('inventory')[:8]
    )

    recent_orders = Order.objects.select_related('user').prefetch_related('items')[:6]

    pending_product_comments = ProductComment.objects.filter(
        is_active=False
    ).select_related('user', 'product').count()

    pending_post_comments = PostComment.objects.filter(
        is_active=False
    ).select_related('user', 'post').count()

    context = {
        'total_products': total_products,
        'total_categories': total_categories,
        'total_orders': total_orders,
        'total_users': total_users,
        'revenue': revenue,
        'bestsellers': bestsellers,
        'low_stock_products': low_stock_products,
        'recent_orders': recent_orders,
        'pending_product_comments': pending_product_comments,
        'pending_post_comments': pending_post_comments,
    }

    return render(request, 'seller_panel/dashboard.html', context)


@staff_member_required
def product_list_view(request):
    products = Product.objects.select_related('category').all().order_by('-created_at')
    return render(request, 'seller_panel/product_list.html', {
        'products': products
    })

@staff_member_required
def product_create_view(request):
    if request.method == 'POST':
        form = SellerProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            messages.success(request, f'محصول «{product.title}» با موفقیت افزوده شد.')
            return redirect('seller_panel:product_list')
    else:
        form = SellerProductForm()

    return render(request, 'seller_panel/product_form.html', {
        'form': form,
        'page_title': 'افزودن محصول جدید'
    })

@staff_member_required
def product_edit_view(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = SellerProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, f'تغییرات محصول «{product.title}» ذخیره شد.')
            return redirect('seller_panel:product_list')
    else:
        form = SellerProductForm(instance=product)

    return render(request, 'seller_panel/product_form.html', {
        'form': form,
        'product': product,
        'page_title': f'ویرایش محصول: {product.title}'
    })

@staff_member_required
def product_delete_view(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        title = product.title
        product.delete()
        messages.success(request, f'محصول «{title}» با موفقیت حذف شد.')
        return redirect('seller_panel:product_list')

    return render(request, 'seller_panel/product_confirm_delete.html', {
        'product': product
    })




@staff_member_required
def category_list_view(request):
    categories = Category.objects.all().order_by('title')
    return render(request, 'seller_panel/category_list.html', {
        'categories': categories
    })

@staff_member_required
def category_create_view(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            category = form.save()
            messages.success(request, f'دسته‌بندی «{category.title}» با موفقیت ایجاد شد.')
            return redirect('seller_panel:category_list')
    else:
        form = CategoryForm()

    return render(request, 'seller_panel/category_form.html', {
        'form': form,
        'page_title': 'افزودن دسته‌بندی جدید'
    })

@staff_member_required
def category_edit_view(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, f'تغییرات دسته‌بندی «{category.title}» ذخیره شد.')
            return redirect('seller_panel:category_list')
    else:
        form = CategoryForm(instance=category)

    return render(request, 'seller_panel/category_form.html', {
        'form': form,
        'category': category,
        'page_title': f'ویرایش دسته‌بندی: {category.title}'
    })

@staff_member_required
def category_delete_view(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        title = category.title
        category.delete()
        messages.success(request, f'دسته‌بندی «{title}» حذف شد.')
        return redirect('seller_panel:category_list')

    return render(request, 'seller_panel/category_confirm_delete.html', {
        'category': category
    })
    
    
@staff_member_required
def order_list_view(request):
    status_filter = request.GET.get('status')
    orders = Order.objects.all().order_by('-created_at')
    if status_filter:
        orders = orders.filter(status=status_filter)
        
    return render(request, 'seller_panel/order_list.html', {
        'orders': orders,
        'status_filter': status_filter,
    })


@staff_member_required
def order_detail_view(request, pk):
    order = get_object_or_404(Order, pk=pk)
    
    if request.method == 'POST':
        form = OrderStatusUpdateForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            messages.success(request, f'وضعیت سفارش #{order.id} با موفقیت به‌روزرسانی شد.')
            return redirect('seller_panel:order_detail', pk=order.pk)
    else:
        form = OrderStatusUpdateForm(instance=order)
        
    return render(request, 'seller_panel/order_detail.html', {
        'order': order,
        'form': form,
    })


@staff_member_required
def comment_list_view(request):
    kind = request.GET.get('kind', 'product')

    if kind == 'product':
        comments = (
            ProductComment.objects
            .select_related('user', 'product', 'parent')
            .order_by('-created_at')
        )
    else:
        comments = (
            PostComment.objects
            .select_related('user', 'post', 'parent')
            .order_by('-created_at')
        )

    return render(request, 'seller_panel/comment_list.html', {
        'comments': comments,
        'kind': kind,
    })


@staff_member_required
def comment_approve_view(request, kind, pk):
    model = ProductComment if kind == 'product' else PostComment

    comment = get_object_or_404(model, pk=pk)
    comment.is_active = True
    comment.save(update_fields=['is_active'])

    messages.success(request, 'نظر با موفقیت تأیید و نمایش داده شد.')
    return redirect(reverse('seller_panel:comment_list') + f'?kind={kind}')


@staff_member_required
def comment_reject_view(request, kind, pk):
    model = ProductComment if kind == 'product' else PostComment

    comment = get_object_or_404(model, pk=pk)
    comment.is_active = False
    comment.save(update_fields=['is_active'])

    messages.info(request, 'نظر به حالت غیرفعال بازگردانده شد.')
    return redirect(reverse('seller_panel:comment_list') + f'?kind={kind}')
