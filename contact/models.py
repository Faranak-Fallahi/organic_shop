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
