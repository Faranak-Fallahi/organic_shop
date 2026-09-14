from django import template

register = template.Library()

@register.filter
def get_item(cart, product_id):
    if not cart:
        return None
    
    # اگر cart یک شیء سشن با دیکشنری cart.cart باشد
    cart_dict = getattr(cart, 'cart', cart)
    
    if not isinstance(cart_dict, dict):
        return None

    # بررسی با کلید رشته‌ای و عددی
    item = cart_dict.get(str(product_id)) or cart_dict.get(int(product_id))
    
    if item:
        if isinstance(item, dict):
            return item.get('quantity', 0)
        return item
    return None
