
from . import forms
from .forms import CustomPasswordResetConfirmForm
from .forms import PhonePasswordResetRequestForm, OTPVerifyForm
from .models import CustomerProfile
from .serializers import CustomerSerializer
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib.auth.views import PasswordChangeView
from django.contrib.messages.views import SuccessMessageMixin
from django.core.cache import cache
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic.edit import FormView
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
import random

User = get_user_model()

def register(request):
    if request.method == "POST":
        form = forms.RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('accounts:login')
    else:
        form = forms.RegisterForm()

    return render(request, 'accounts/register.html', {'form': form})


class UserLoginView(LoginView):
    template_name = "accounts/login.html"




@login_required
def profile_view(request):
    user = request.user

    if request.method == "POST":
        form = forms.ProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            

            return redirect("product_list")
    
    else:
        
        form = forms.ProfileForm(instance=user)

    return render(request, "accounts/profile.html", {"form": form})


class CustomPasswordChangeView(SuccessMessageMixin, PasswordChangeView):
    template_name = 'accounts/password_change.html'
    form_class = forms.CustomPasswordChangeForm
    success_url = reverse_lazy('accounts:profile')  
    success_message = "رمز عبور شما با موفقیت تغییر کرد."
    
    
    
    
#  مرحله درخواست کد
class PhonePasswordResetRequestView(FormView):
    template_name = "accounts/password_reset_request.html"
    form_class = PhonePasswordResetRequestForm
    success_url = reverse_lazy("accounts:password_reset_verify")

    def form_valid(self, form):
        phone = form.cleaned_data["phone"]

        # بررسی وجود کاربر با این شماره
        user_exists = User.objects.filter(phone=phone).exists()

        # تولید OTP
        otp_code = str(random.randint(10000, 99999))

        # ذخیره در cache (120 ثانیه)
        cache.set(f"reset_otp_{phone}", otp_code, timeout=120)

        # ذخیره شماره در session
        self.request.session["reset_phone"] = phone

        # در حالت واقعی اینجا باید پیامک ارسال شود
        print(f"--- SMS Code for {phone}: {otp_code} ---")

        # برای امنیت: حتی اگر کاربر وجود نداشت، پیام عمومی بده
        messages.success(
            self.request,
            "اگر شماره وارد شده در سیستم وجود داشته باشد، کد تایید ارسال شد."
        )

        return super().form_valid(form)

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))
    
    

#  مرحله تایید کد
class OTPVerifyView(View):
    def get(self, request):
        if 'reset_phone' not in request.session: 
            return redirect('accounts:password_reset_request')
        return render(request, 'accounts/password_reset_otp_verify.html', {'form': OTPVerifyForm()})

    def post(self, request):
        # 1. مطمئن شو شماره موبایل دقیقاً همان چیزی است که در سشن ذخیره شده
        phone = request.session.get('reset_phone')
        
        if not phone:
            return redirect('accounts:password_reset_request')

        form = OTPVerifyForm(request.POST)
        
        if form.is_valid():
            user_code = form.cleaned_data['code'].strip() # استفاده از strip برای حذف فضاها
            
            # 2. تولید دقیق کلید کش (مطمئن شو فضای اضافه ندارد)
            cache_key = f"reset_otp_{phone}"
            cached_code = cache.get(cache_key)
            
            # --- دیباگ در کنسول (بسیار مهم) ---
            print(f"DEBUG: Phone from session: '{phone}'")
            print(f"DEBUG: Looking for Key: '{cache_key}'")
            print(f"DEBUG: User entered: '{user_code}'")
            print(f"DEBUG: Code found in cache: '{cached_code}'")
            # ----------------------------------

            if cached_code and str(cached_code) == str(user_code):
                request.session['otp_verified'] = True
                return redirect('accounts:password_reset_confirm')
            
            if not cached_code:
                form.add_error('code', 'کد منقضی شده است. لطفا دوباره درخواست دهید.')
            else:
                form.add_error('code', 'کد وارد شده اشتباه است.')
        
        return render(request, 'accounts/password_reset_otp_verify.html', {'form': form})


# مرحله تنظیم رمز جدید

class SetNewPasswordView(View):
    def get_user(self, request):
        phone = request.session.get('reset_phone')
        try:
            return User.objects.get(phone=phone) # یا phone_number مطابق مدل شما
        except (User.DoesNotExist, TypeError):
            return None

    def get(self, request):
        if not request.session.get('otp_verified'):
            return redirect('accounts:password_reset_request')
        
        user = self.get_user(request)
        if not user:
            return redirect('accounts:password_reset_request')

        # استفاده از فرم مخصوص تنظیم رمز بدون نیاز به رمز قدیمی
        form = CustomPasswordResetConfirmForm(user=user)
        return render(request, 'accounts/password_reset_confirm.html', {'form': form})

    def post(self, request):
        if not request.session.get('otp_verified'):
            return redirect('accounts:password_reset_request')

        user = self.get_user(request)
        form = CustomPasswordResetConfirmForm(user=user, data=request.POST)
        
        if form.is_valid():
            form.save() # این متد بصورت خودکار پسورد کاربر را عوض و ذخیره می‌کند

            # پاکسازی سشن
            request.session.pop('reset_phone', None)
            request.session.pop('otp_verified', None)
            request.session.pop('sent_otp', None)

            messages.success(request, "رمز عبور شما با موفقیت تغییر کرد.")
            return redirect('accounts:login')
        
        return render(request, 'accounts/password_reset_confirm.html', {'form': form})

class CustomerViewSet(ModelViewSet):
    serializer_class = CustomerSerializer
    queryset = CustomerProfile.objects.all()
    permission_classes = [IsAuthenticated]

    @action(detail=False)
    def me(self, request):
        user_id = request.user.id
        customer = CustomerProfile.objects.get (user_id=user_id)
        serializer = self.get_serializer(customer)
        return Response(serializer.data)
