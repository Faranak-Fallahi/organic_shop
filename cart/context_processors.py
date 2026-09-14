from .models import Cart, CartItem


def get_or_create_cart(request):
  if request.user.is_authenticated:
    cart, _ = Cart.objects.get_or_create(user=request.user)
    # اگر قبل از لاگین سبدی در سشن داشته، آن را به کاربر وصل می‌کنیم
    session_cart_id = request.session.get('cart_id')
    if session_cart_id and str(cart.id) != str(session_cart_id):
      session_cart = (
          Cart.objects.filter(id=session_cart_id, user__isnull=True)
          .prefetch_related('items')
          .first()
      )
      if session_cart:
        for item in session_cart.items.all():
          cart_item, created = CartItem.objects.get_or_create(
              cart=cart,
              product=item.product,
              defaults={'quantity': item.quantity},
          )
          if not created:
            cart_item.quantity += item.quantity
            cart_item.save(update_fields=['quantity'])
        session_cart.delete()
        del request.session['cart_id']
        request.session.modified = True
    return cart

  cart_id = request.session.get('cart_id')
  if cart_id:
    cart = (
        Cart.objects.filter(id=cart_id, user__isnull=True)
        .prefetch_related('items__product')
        .first()
    )
    if cart:
      return cart

  cart = Cart.objects.create()
  request.session['cart_id'] = str(cart.id)
  request.session.modified = True
  return cart


def cart_context(request):
  cart = get_or_create_cart(request)
  items = (
      cart.items.select_related('product').all() if cart else CartItem.objects.none()
  )

  return {
      'cart': cart,
      'cart_items': items,
      'cart_total_price': cart.get_total_price() if cart else 0,
      'cart_count': cart.get_total_quantity() if cart else 0,
  }
