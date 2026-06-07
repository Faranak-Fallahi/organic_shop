from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User


class RegisterForm(UserCreationForm):
    username = forms.CharField(
        label="نام کاربری",
        widget=forms.TextInput(attrs={
            "placeholder": "نام کاربری خود را وارد کنید"
        })
    )

    email = forms.EmailField(
        label="ایمیل",
        widget=forms.EmailInput(attrs={
            "placeholder": "ایمیل خود را وارد کنید"
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
        fields = ['username', 'email', 'phone', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'form-input'
            })
