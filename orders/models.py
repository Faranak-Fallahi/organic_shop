from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
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
    
   
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=15)
    address = models.TextField()
    postal_code = models.CharField(max_length=10)
    
    
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
    # ذخیره قیمت در لحظه خرید
    price = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    def __str__(self):
        return f"{self.product.name} (x{self.quantity})"

   
    @property
    def total_price(self):
        return self.price * self.quantity
    