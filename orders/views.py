from decimal import Decimal, ROUND_HALF_UP

from django.core.exceptions import ValidationError
from django.db import transaction
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from cart.models import Cart, CartItem
from .forms import CheckoutForm
from .models import Order, OrderItem
from .serializers import (
    OrderCreateSerializer,
    OrderForAdminSerializer,
    OrderSerializer,
    OrderUpdateSerializer,
)


class OrderViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete', 'options', 'head']

    def get_permissions(self):
        if self.request.method in ['PATCH', 'DELETE']:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def get_queryset(self):
        from django.db.models import Prefetch
        queryset = Order.objects.select_related('user').prefetch_related(
            Prefetch(
                'items',
                queryset=OrderItem.objects.select_related('product')
            )
        )
        user = self.request.user
        if user.is_staff:
            return queryset
        return queryset.filter(user=user)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return OrderCreateSerializer
        if self.request.method == 'PATCH':
            return OrderUpdateSerializer
        if self.request.user.is_staff:
            return OrderForAdminSerializer
        return OrderSerializer

    def get_serializer_context(self):
        return {'request': self.request}

    def create(self, request, *args, **kwargs):
        create_order_serializer = OrderCreateSerializer(
            data=request.data,
            context={'request': request},
        )
        create_order_serializer.is_valid(raise_exception=True)
        created_order = create_order_serializer.save()

        serializer = OrderSerializer(created_order, context={'request': request})
        return Response(serializer.data)


@login_required(login_url='accounts:auth_request')
def order_create_view(request):
    cart = Cart.objects.filter(user=request.user).first()

    if not cart or not cart.items.exists():
        messages.warning(request, 'سبد خرید شما خالی است.')
        return redirect('store:product-page')

    if request.method == 'GET':
        form = CheckoutForm(user=request.user)
        cart_items = cart.items.select_related('product').all()
        total = cart.get_total_price()
        total_base = cart.get_total_base_price()
        discount = cart.get_total_discount()
        return render(request, 'order/order_checkout.html', {
            'form': form,
            'cart_items': cart_items,
            'cart': cart,
            'total': total,
            'total_base': total_base,
            'discount': discount,
        })

    form = CheckoutForm(user=request.user, data=request.POST)
    if not form.is_valid():
        cart_items = cart.items.select_related('product').all()
        return render(request, 'order/order_checkout.html', {
            'form': form,
            'cart_items': cart_items,
            'cart': cart,
            'total': cart.get_total_price(),
            'total_base': cart.get_total_base_price(),
            'discount': cart.get_total_discount(),
        })

    cart_items = cart.items.select_related('product').all()
    checkout_context = {
        'form': form,
        'cart_items': cart_items,
        'cart': cart,
        'total': cart.get_total_price(),
        'total_base': cart.get_total_base_price(),
        'discount': cart.get_total_discount(),
    }

    try:
        with transaction.atomic():
            order = Order.objects.create(
                user=request.user,
                first_name=form.cleaned_data.get('first_name', ''),
                last_name=form.cleaned_data.get('last_name', ''),
                phone=form.cleaned_data.get('phone', ''),
                city=form.cleaned_data.get('city', ''),
                postal_code=form.cleaned_data.get('postal_code', ''),
                address=form.cleaned_data.get('address', ''),
            )

            order_items = []
            for item in cart_items:
                if not item.product.is_active:
                    raise ValidationError(
                        f'محصول «{item.product.title}» فعال نیست.'
                    )
                order_items.append(OrderItem(
                    order=order,
                    product=item.product,
                    base_price=item.product.price,
                    price=item.product.final_price,
                    quantity=item.quantity,
                ))
            OrderItem.objects.bulk_create(order_items)

            order.reserve_inventory()

            cart.items.all().delete()
            cart.delete()

            try:
                del request.session['cart_id']
                request.session.modified = True
            except KeyError:
                pass
    except ValidationError as exc:
        messages.error(request, str(exc))
        return render(request, 'order/order_checkout.html', checkout_context)

    form.save_profile(request.user)

    messages.success(request, f'سفارش شماره {order.id} با موفقیت ثبت شد.')
    return redirect('orders:order-payment', order_id=order.id)


@login_required(login_url='accounts:auth_request')
def order_list_view(request):
    orders = (
        Order.objects
        .filter(user=request.user)
        .order_by("-created_at")
        .prefetch_related('items__product')
    )
    return render(
        request,
        "order/order_list.html",
        {"orders": orders},
    )


@login_required(login_url='accounts:auth_request')
def order_detail_view(request, order_id):
    order = get_object_or_404(
        Order.objects.prefetch_related("items__product"),
        id=order_id,
        user=request.user,
    )
    return render(request, "order/order_detail.html", {
        "order": order,
    })


@login_required(login_url='accounts:auth_request')
def order_payment_view(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if order.status == Order.ORDER_STATUS_CANCELED:
        messages.error(request, 'این سفارش لغو شده است و امکان پرداخت ندارد.')
        return redirect('orders:order-detail', order_id=order.id)

    if order.status == Order.ORDER_STATUS_PAID:
        messages.info(request, "این سفارش قبلاً پرداخت شده است.")
        return redirect("orders:order-detail", order_id=order.id)

    items = order.items.select_related('product').all()
    return render(request, "order/fake_payment_gateway.html", {
        "order": order,
        "items": items,
    })


@login_required(login_url='accounts:auth_request')
def order_payment_callback_view(request, order_id):
    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user
    )

    status = request.GET.get("status")

    if order.status == Order.ORDER_STATUS_CANCELED:
        messages.error(request, 'این سفارش لغو شده است و امکان پرداخت ندارد.')
        return redirect('orders:order-detail', order_id=order.id)

    if status == "success" and order.status != Order.ORDER_STATUS_PAID:
        with transaction.atomic():
            order.refresh_from_db()
            if order.status == Order.ORDER_STATUS_PAID:
                messages.info(request, "پرداخت این سفارش قبلاً تأیید شده است.")
                return redirect("orders:order-detail", order_id=order.id)

            order.status = Order.ORDER_STATUS_PAID
            order.save(update_fields=['status'])
            messages.success(request, 'پرداخت با موفقیت تأیید شد.')

    return redirect("orders:order-detail", order_id=order.id)