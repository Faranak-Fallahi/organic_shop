from decimal import Decimal, ROUND_HALF_UP, InvalidOperation

from django import template

register = template.Library()


_FA_DIGITS = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")


def _to_fa(value):
    """تبدیل عدد به نمایش فارسی با جداکننده سه‌رقمی فارسی."""
    if value is None or value == "":
        return ""
    try:
        decimal_value = Decimal(str(value)).quantize(
            Decimal('1'), rounding=ROUND_HALF_UP
        )
    except (ValueError, TypeError, InvalidOperation):
        return value

    sign = ""
    if decimal_value < 0:
        sign = "−"
        decimal_value = abs(decimal_value)

    return sign + format(decimal_value, ',.0f').replace(',', '٬').translate(_FA_DIGITS)


@register.filter
def fa_num(value):
    """عدد فارسی: 123456 -> ۱۲۳٬۴۵۶"""
    return _to_fa(value)


@register.filter
def fa_price(value):
    """قیمت تومانی فارسی: 123456 -> ۱۲۳٬۴۵۶ تومان"""
    fa = _to_fa(value)
    if fa == "":
        return ""
    return f"{fa} تومان"


@register.filter
def product_base_price(product):
    if product:
        return product.base_price
    return None


@register.filter
def product_final_price(product):
    if product:
        return product.final_price
    return None


@register.filter
def has_discount(product):
    return bool(product and product.discount and product.discount > 0)


@register.filter
def discount_percent(product):
    if product and product.discount and product.discount > 0:
        return product.discount
    return 0