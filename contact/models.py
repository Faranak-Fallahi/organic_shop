from django.db import models


class Branch(models.Model):
    title = models.CharField(max_length=200, verbose_name="عنوان شعبه")
    phone = models.CharField(
        max_length=50, blank=True, verbose_name="تلفن تماس"
    )
    whatsapp = models.CharField(
        max_length=50, blank=True, verbose_name="شماره واتساپ"
    )
    working_hours = models.CharField(
        max_length=150, blank=True, verbose_name="روزها و ساعات کاری"
    )
    address = models.TextField(verbose_name="آدرس کامل")
    neshan_link = models.URLField(
        blank=True, verbose_name="لینک مسیریابی در نشان"
    )
    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب نمایش")
    is_active = models.BooleanField(default=True, verbose_name="فعال باشد؟")

    class Meta:
        verbose_name = "شعبه"
        verbose_name_plural = "شعبه‌ها"
        ordering = ["order", "id"]

    def __str__(self):
        return self.title

from django.db import models


class AboutPage(models.Model):
    hero_title = models.CharField(
        max_length=200,
        default="داستان عطاری آویشن"
    )
    hero_subtitle = models.CharField(
        max_length=300,
        blank=True
    )
    brand_name = models.CharField(
        max_length=150,
        default="عطاری آویشن"
    )
    brand_description = models.CharField(
        max_length=250,
        blank=True
    )
    logo = models.Image_title(
        upload_to="about/",
        blank=True,
        null=True
    )
    story_title = models.CharField(
        max_length=250,
        default="داستان ما و تعهد به سلامت شما"
    )
    story_text_1 = models.TextField(blank=True)
    story_text_2 = models.TextField(blank=True)
    products_title = models.CharField(
        max_length=250,
        default="تنوع محصولات در عطاری آنلاین آویشن"
    )
    products_description = models.TextField(blank=True)

    class Meta:
        verbose_name = "صفحه درباره ما"
        verbose_name_plural = "صفحه درباره ما"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def __str__(self):
        return "محتوای صفحه درباره ما"


class AboutFeature(models.Model):
    about_page = models.ForeignKey(
        AboutPage,
        on_delete=models.CASCADE,
        related_name="features"
    )
    title = models.CharField(max_length=150)
    description = models.TextField()
    icon = models.CharField(
        max_length=100,
        default="bi bi-check-circle"
    )
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "ویژگی صفحه درباره ما"
        verbose_name_plural = "ویژگی‌های صفحه درباره ما"

    def __str__(self):
        return self.title


class AboutCategory(models.Model):
    about_page = models.ForeignKey(
        AboutPage,
        on_delete=models.CASCADE,
        related_name="categories"
    )
    title = models.CharField(max_length=150)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "دسته‌بندی صفحه درباره ما"
        verbose_name_plural = "دسته‌بندی‌های صفحه درباره ما"

    def __str__(self):
        return self.title
