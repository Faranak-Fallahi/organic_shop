from django.conf import settings
from django.db import models
from store.models import Product
import uuid


class Cart(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='cart',
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart - {self.user}"

    def get_total_price(self):
        return sum(item.get_total_price() for item in self.items.all())

    def get_total_base_price(self):
        return sum(item.get_total_base_price() for item in self.items.all())

    def get_total_discount(self):
        return self.get_total_base_price() - self.get_total_price()


    def get_total_quantity(self):
        return sum(item.quantity for item in self.items.all())
    
    
class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='cart_items'
    )
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['cart', 'product']

    def __str__(self):
        return f"{self.product} x {self.quantity}"
    
    
    def get_total_price(self):
        """قیمت نهایی (تخفیف‌خورده) کل این آیتم."""
        return self.product.final_price * self.quantity

    def get_total_base_price(self):
        """مجموع قیمت قبلی (بدون تخفیف) این آیتم."""
        return self.product.price * self.quantity
