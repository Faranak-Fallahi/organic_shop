from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm, SetPasswordForm, UserCreationForm
from .models import CustomerProfile
import re

User = get_user_model()

class StyledAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        label="نام کاربری",
        widget=forms.TextInput(attrs={"placeholder": "نام کاربری خود را وارد کنید"}),
    )
    password = forms.CharField(
        label="رمز عبور",
        widget=forms.PasswordInput(attrs={"placeholder": "رمز عبور خود را وارد کنید"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-input"})

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
        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': 'نام'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'نام خانوادگی'}),
            'phone': forms.TextInput(attrs={'placeholder': '۰۹۱۲۳۴۵۶۷۸۹', 'dir': 'ltr'}),
            'email': forms.EmailInput(attrs={'placeholder': 'example@email.com', 'dir': 'ltr'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-input'})


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
            'city': forms.TextInput(attrs={'placeholder': 'مثال: تهران'}),
            'postal_code': forms.TextInput(attrs={'placeholder': 'مثال: ۱۲۳۴۵۶۷۸۹۰', 'dir': 'ltr'}),
            'address': forms.Textarea(attrs={
                'placeholder': 'آدرس محل سکونت جهت ارسال محصولات',
                'rows': 3,
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-input'})



class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-input'})



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
