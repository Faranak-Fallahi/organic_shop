from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordChangeForm, SetPasswordForm, UserCreationForm
from .models import CustomerProfile
import re

User = get_user_model()


# فرم ورود یا ثبت‌نام سریع با شماره موبایل
class PhoneLoginForm(forms.Form):
    phone = forms.CharField(
        max_length=11,
        label="شماره موبایل",
        widget=forms.TextInput(attrs={
            'placeholder': 'مثال: 09123456789',
            'class': 'form-input',
            'dir': 'ltr'
        })
    )

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '').strip()
        persian_digits = '۰۱۲۳۴۵۶۷۸۹'
        for i, digit in enumerate(persian_digits):
            phone = phone.replace(digit, str(i))

        if not re.match(r'^09\d{9}$', phone):
            raise forms.ValidationError('لطفاً شماره موبایل معتبر ۱۱ رقمی وارد کنید.')
        return phone


# فرم ثبت‌نام عادی با نام کاربری و رمز عبور
class RegisterForm(UserCreationForm):
    username = forms.CharField(
        label="نام کاربری",
        widget=forms.TextInput(attrs={"placeholder": "نام کاربری خود را وارد کنید"})
    )
    phone = forms.CharField(
        label="شماره موبایل",
        widget=forms.TextInput(attrs={"placeholder": "مثال: 09123456789"})
    )

    class Meta:
        model = User
        fields = ['username', 'phone']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-input'})


# فرم اطلاعات کاربری اصلی
class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone', 'email']
        labels = {
            'first_name': 'نام',
            'last_name': 'نام خانوادگی',
            'phone': 'شماره موبایل',
            'email': 'ایمیل',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-input'})


# فرم پروفایل مشتری (آدرس و کد پستی)
class ProfileForm(forms.ModelForm):
    class Meta:
        model = CustomerProfile
        fields = ['city', 'postal_code', 'address']
        labels = {
            'city': 'شهر',
            'postal_code': 'کد پستی',
            'address': 'آدرس دقیق',
        }
        widgets = {
            'address': forms.Textarea(attrs={
                'placeholder': 'آدرس محل سکونت جهت ارسال محصولات عطاری',
                'rows': 3
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-input'})


# فرم تغییر رمز عبور
class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-input'})


# فرم درخواست کد برای فراموشی رمز عبور
class PhonePasswordResetRequestForm(forms.Form):
    phone = forms.CharField(
        max_length=11,
        label="شماره موبایل",
        widget=forms.TextInput(attrs={'placeholder': 'مثال: 09123456789'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-input'})

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '').strip()
        if not User.objects.filter(phone=phone).exists():
            raise forms.ValidationError("کاربری با این شماره تلفن یافت نشد.")
        return phone


# فرم تایید کد تایید (OTP)
class OTPVerifyForm(forms.Form):
    code = forms.CharField(
        max_length=6,
        label="کد تایید",
        widget=forms.TextInput(attrs={
            'placeholder': 'کد تایید را وارد کنید',
            'dir': 'ltr'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'form-input',
                'style': 'text-align: center; letter-spacing: 5px;'
            })


# فرم ساخت رمز عبور جدید
class CustomPasswordResetConfirmForm(SetPasswordForm):
    new_password1 = forms.CharField(
        label="رمز عبور جدید",
        widget=forms.PasswordInput(attrs={
            "class": "form-input",
            "placeholder": "رمز عبور جدید را وارد کنید",
            "autocomplete": "new-password",
        }),
        strip=False,
        help_text="رمز عبور باید حداقل ۸ کاراکتر باشد و کاملاً عددی نباشد."
    )

    new_password2 = forms.CharField(
        label="تکرار رمز عبور جدید",
        widget=forms.PasswordInput(attrs={
            "class": "form-input",
            "placeholder": "رمز عبور جدید را دوباره وارد کنید",
            "autocomplete": "new-password",
        }),
        strip=False,
        help_text="برای تأیید، رمز عبور جدید را دوباره وارد کنید."
    )

    def __init__(self, user, *args, **kwargs):
        super().__init__(user, *args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-input"})
