from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User
from django.contrib.auth import get_user_model


class RegisterForm(UserCreationForm):
    username = forms.CharField(
        label="نام کاربری",
        widget=forms.TextInput(attrs={
            "placeholder": "نام کاربری خود را وارد کنید"
        })
    )

 

    phone = forms.CharField(
        label="شماره موبایل",
        widget=forms.TextInput(attrs={
            "placeholder": "مثال: 09123456789"
        })
    )

    password1 = forms.CharField(
        label="رمز عبور",
        widget=forms.PasswordInput(attrs={
            "placeholder": "رمز عبور"
        })
    )

    password2 = forms.CharField(
        label="تکرار رمز عبور",
        widget=forms.PasswordInput(attrs={
            "placeholder": "تکرار رمز عبور"
        })
    )

    class Meta:
        model = User
        fields = ['username',  'phone', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'form-input'
            })

User = get_user_model()

class ProfileForm(forms.ModelForm):
   

    phone = forms.CharField(
        label="شماره موبایل",
        widget=forms.TextInput(attrs={
            "placeholder": "مثال: 09123456789"
        })
    )

    address = forms.CharField(
        label="آدرس دقیق",
        required=False,
        widget=forms.Textarea(attrs={
            "placeholder": "آدرس محل سکونت جهت ارسال محصولات عطاری",
            "rows": 3  # برای اینکه آدرس فضای بیشتری داشته باشد
        })
    )

    class Meta:
        model = User
        fields = [ "phone", "address"]

    def __init__(self, *args, **kwargs):
        # اول فراخوانی متد اصلی کلاس پدر
        super().__init__(*args, **kwargs)

        # اضافه کردن خودکار کلاس 'form-input' به تمام فیلدها (مثل فرم ثبت‌نام)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'form-input'
            })