from .models import User
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.forms import UserCreationForm

# فرم ثبت نام
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

# فرم پروفایل کاربر
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
            
# فرم تغییر رمز عبور        
class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            # اینجا چک کن که کلاس دقیقاً همان کلاسی باشد که در CSS داری (مثلاً form-input یا form-control)
            field.widget.attrs.update({
                'class': 'form-input', 
                'style': 'width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; box-sizing: border-box;'
            })

# فرم درخواست پیامک (وارد کردن شماره موبایل)
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
        phone = self.cleaned_data.get('phone')
        if not User.objects.filter(phone=phone).exists():
            raise forms.ValidationError("کاربری با این شماره تلفن یافت نشد.")
        return phone



# فرم تایید کد ارسال شده (OTP)
class OTPVerifyForm(forms.Form):
    code = forms.CharField(
        max_length=6,
        label="کد تایید",
        widget=forms.TextInput(attrs={'placeholder': 'کد ۶ رقمی را وارد کنید'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'form-input',
                'style': 'text-align: center; letter-spacing: 5px;' # استایل‌های خاص را اینجا نگه دار
            })
            
# فرم ساخت رمز جدید برای فراموشی رمز عبور
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
            field.widget.attrs.update({
                "class": "form-input",
            })