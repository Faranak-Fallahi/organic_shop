from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from decimal import Decimal, ROUND_HALF_UP
from store.models import Product


class Order(models.Model):
    ORDER_STATUS_PENDING = 'pending'
    ORDER_STATUS_PAID = 'paid'
    ORDER_STATUS_SHIPPED = 'shipped'
    ORDER_STATUS_CANCELED = 'canceled'

    STATUS_CHOICES = [
        (ORDER_STATUS_PENDING, 'در انتظار پرداخت'),
        (ORDER_STATUS_PAID, 'پرداخت شده'),
        (ORDER_STATUS_SHIPPED, 'ارسال شده'),
        (ORDER_STATUS_CANCELED, 'لغو شده'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='orders',
    )
    first_name = models.CharField(max_length=255, blank=True, default='')
    last_name = models.CharField(max_length=255, blank=True, default='')
    phone = models.CharField(max_length=15, blank=True, default='')
    city = models.CharField(max_length=100, blank=True, default='')
    address = models.TextField(blank=True, default='')
    postal_code = models.CharField(max_length=10, blank=True, default='')

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=ORDER_STATUS_PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"سفارش شماره {self.id} - {self.first_name} {self.last_name}"

    @property
    def total_price(self):
        return sum(item.total_price for item in self.items.all())

    @property
    def total_base_price(self):
        return sum(
            (item.base_price or item.price or 0) * item.quantity
            for item in self.items.all()
        )

    @property
    def total_discount(self):
        return self.total_base_price - self.total_price

    @property
    def get_total_price(self):
        return self.total_price

    @property
    def status_label(self):
        labels = dict(self.STATUS_CHOICES)
        return labels.get(self.status, self.status)

    @property
    def status_class(self):
        cls = {
            'pending': 'pending',
            'paid': 'paid',
            'shipped': 'shipped',
            'canceled': 'canceled',
        }
        return cls.get(self.status, 'pending')

    def has_address(self):
        return bool(self.first_name or self.address)


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name='order_items'
    )
    quantity = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1)]
    )
    base_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='قیمت قبل از تخفیف در زمان خرید'
    )
    price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='قیمت نهایی (تخفیف‌خورده) در زمان خرید'
    )

    def __str__(self):
        return f"{self.product.title} (x{self.quantity})"

    @property
    def total_price(self):
        if self.price and self.quantity:
            return self.price * self.quantity
        return 0

    @property
    def total_base_price(self):
        if self.base_price and self.quantity:
            return self.base_price * self.quantity
        return self.total_price

    @property
    def item_discount(self):
        return self.total_base_price - self.total_price

    @property
    def has_discount(self):
        return bool(self.base_price and self.price and self.base_price > self.price)

    @property
    def get_cost(self):
        return self.total_price

    def save(self, *args, **kwargs):
        if not self.price and self.product:
            self.price = self.product.final_price
        if not self.base_price and self.product:
            self.base_price = self.product.price
        super().save(*args, **kwargs)
