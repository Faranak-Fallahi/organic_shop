
from decimal import Decimal, ROUND_HALF_UP
from django.conf import settings
from django.db import models
from django.utils.text import slugify

class Category(models.Model):
    title = models.CharField(max_length=100, verbose_name='عنوان دسته‌بندی')
    slug = models.SlugField(unique=True, blank=True)
    image = models.ImageField(
        upload_to='categories/',
        null=True,
        blank=True,
        verbose_name='تصویر دسته‌بندی'
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title, allow_unicode=True)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ("title",)
        verbose_name = "دسته‌بندی"
        verbose_name_plural = "دسته‌بندی‌ها"


class Product(models.Model):
    UNIT_GRAMS = 'گرم'
    UNIT_KILO = 'کیلو'
    UNIT_COUNT = 'عدد'
    UNIT_PACK = 'بسته'
    UNIT_PACKET = 'نخ'
    UNIT_DRAM = 'پاکت'

    UNIT_CHOICES = [
        (UNIT_GRAMS, 'گرم'),
        (UNIT_KILO, 'کیلوگرم'),
        (UNIT_COUNT, 'عدد'),
        (UNIT_PACK, 'بسته'),
        (UNIT_PACKET, 'نخ'),
        (UNIT_DRAM, 'پاکت'),
    ]

    category = models.ForeignKey(
        Category,
        related_name="products",
        on_delete=models.CASCADE,
        verbose_name='دسته‌بندی'
    )
    title = models.CharField(max_length=200, verbose_name='نام محصول')
    slug = models.SlugField(unique=True, blank=True)
    image = models.ImageField(
        upload_to='products/',
        null=True,
        blank=True,
        verbose_name='تصویر محصول'
    )
    description = models.TextField(blank=True, verbose_name='توضیحات')

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='قیمت'
    )
       
    inventory = models.PositiveIntegerField(default=0, verbose_name='موجودی انبار')
    min_order_quantity = models.PositiveIntegerField(default=1, verbose_name="حداقل مقدار سفارش")
    discount = models.PositiveIntegerField(
        default=0,
        verbose_name='درصد تخفیف'
    )

    unit = models.CharField(
        max_length=20,
        choices=UNIT_CHOICES,
        default=UNIT_KILO,
        verbose_name='واحد فروش'
    )

    is_special = models.BooleanField(
        default=False,
        verbose_name='فروش ویژه'
    )

    is_active = models.BooleanField(default=True, verbose_name='وضعیت فعال')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def discounted_price(self):
        if self.discount > 0:
            discount_amount = (
                self.price * Decimal(self.discount)
            ) / Decimal('100')
            return self.price - discount_amount
        return self.price

    @property
    def has_discount(self):
        return self.discount > 0

    @property
    def base_price(self):
        return self.price

    @property
    def _decimal_price(self):
        try:
            return Decimal(str(self.price))
        except (ValueError, TypeError):
            return Decimal('0')

    @property
    def discount_amount(self):
        if self.discount > 0:
            amount = (self._decimal_price * Decimal(self.discount)) / Decimal('100')
            return amount.quantize(Decimal('1'), rounding=ROUND_HALF_UP)
        return Decimal('0')

    @property
    def final_price(self):
        """قیمت نهایی تخفیف‌خورده؛ مبنای همه محاسبات Cart/Order."""
        if self.discount > 0:
            amount = (self._decimal_price * Decimal(100 - self.discount)) / Decimal('100')
            return amount.quantize(Decimal('1'), rounding=ROUND_HALF_UP)
        return self._decimal_price.quantize(Decimal('1'), rounding=ROUND_HALF_UP)

    @property
    def formatted_price(self):
        try:
            return f"{int(self._decimal_price):,}"
        except (ValueError, TypeError):
            return self.price

    @property
    def formatted_final_price(self):
        try:
            return f"{int(self.final_price):,}"
        except Exception:
            return self.final_price
        
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title, allow_unicode=True) or "product"
            slug = base_slug
            counter = 1
            while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "محصول"
        verbose_name_plural = "محصولات"


class Favorite(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='favorites'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='favorites'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')
        verbose_name = 'محصول مورد علاقه'
        verbose_name_plural = 'محصولات مورد علاقه'

    def __str__(self):
        return f'{self.user} - {self.product.title}'
