
from . import forms, otp
from .forms import CustomPasswordResetConfirmForm,OTPVerifyForm,PhonePasswordResetRequestForm
from .models import CustomerProfile
from .serializers import CustomerSerializer

from comments.models import ProductComment, PostComment
from orders.models import Order
from store.models import Favorite

from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic.edit import FormView

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

import re


User = get_user_model()


def normalize_phone(phone):
    phone = phone.translate(
        str.maketrans(
            "۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩",
            "01234567890123456789",
        )
    )

    phone = re.sub(r"\s+", "", phone)
    return phone


def register(request):
    if request.method == "POST":
        form = forms.RegisterForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("accounts:login")
    else:
        form = forms.RegisterForm()

    return render(
        request,
        "auth/register.html",
        {"form": form},
    )


class UserLoginView(LoginView):
    template_name = "auth/login.html"
    authentication_form = forms.StyledAuthenticationForm


class UserLogoutView(LogoutView):
    http_method_names = ['post', 'options']


@login_required
def dashboard_view(request):
    user = request.user

    CustomerProfile.objects.get_or_create(user=user)

    orders = Order.objects.filter(user=user).prefetch_related('items')

    total_orders = orders.count()
    paid_orders = orders.filter(status__in=['paid', 'shipped'])
    pending_orders = orders.filter(status='pending')

    total_spent = sum(order.total_price for order in paid_orders)

    recent_orders = orders.order_by('-created_at')[:5]

    favorites_count = Favorite.objects.filter(user=user).count()

    product_comments_count = ProductComment.objects.filter(user=user).count()
    approved_product_comments = ProductComment.objects.filter(
        user=user, is_active=True
    ).count()

    context = {
        'user': user,
        'total_orders': total_orders,
        'paid_orders_count': paid_orders.count(),
        'pending_orders_count': pending_orders.count(),
        'total_spent': total_spent,
        'recent_orders': recent_orders,
        'favorites_count': favorites_count,
        'product_comments_count': product_comments_count,
        'approved_product_comments': approved_product_comments,
    }

    return render(request, 'auth/user_dashboard.html', context)


@login_required
def my_comments_view(request):
    product_comments = (
        ProductComment.objects
        .filter(user=request.user)
        .select_related('product')
        .order_by('-created_at')
    )

    post_comments = (
        PostComment.objects
        .filter(user=request.user)
        .select_related('post')
        .order_by('-created_at')
    )

    return render(
        request,
        'auth/my_comments.html',
        {
            'product_comments': product_comments,
            'post_comments': post_comments,
        },
    )


@login_required
def profile_view(request):
    user = request.user

    user_form = forms.UserUpdateForm(
        request.POST or None,
        instance=user,
    )

    customer_profile, created = CustomerProfile.objects.get_or_create(
        user=user
    )

    profile_form = forms.ProfileForm(
        request.POST or None,
        instance=customer_profile,
    )

    if request.method == "POST":
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()

            messages.success(
                request,
                "اطلاعات حساب شما با موفقیت ذخیره شد.",
            )

            return redirect("accounts:profile")

    return render(
        request,
        "auth/profile.html",
        {
            "user_form": user_form,
            "profile_form": profile_form,
            "form": profile_form,
        },
    )


class CustomPasswordChangeView(
    SuccessMessageMixin,
    PasswordChangeView,
):
    template_name = "auth/password_change.html"
    form_class = forms.CustomPasswordChangeForm
    success_url = reverse_lazy("accounts:profile")
    success_message = "رمز عبور شما با موفقیت تغییر کرد."


class PhonePasswordResetRequestView(FormView):
    template_name = "auth/password_reset_request.html"
    form_class = PhonePasswordResetRequestForm
    success_url = reverse_lazy("accounts:password_reset_verify")

    def form_valid(self, form):
        phone = normalize_phone(
            form.cleaned_data["phone"]
        )

        key = f"reset_{phone}"

        if otp.is_resend_blocked(key):
            messages.error(
                self.request,
                "لطفاً کمی صبر کنید و سپس دوباره درخواست دهید.",
            )
            return super().form_valid(form)

        if otp.too_many_requests(key):
            messages.error(
                self.request,
                "تعداد درخواست‌های شما بیش از حد مجاز است. "
                "لطفاً بعداً دوباره تلاش کنید.",
            )
            return super().form_valid(form)

        self.request.session["reset_phone"] = phone

        if not User.objects.filter(phone=phone).exists():
            messages.info(
                self.request,
                "اگر شماره واردشده در سیستم وجود داشته باشد، "
                "کد تأیید در ترمینال نمایش داده شد.",
            )
            return super().form_valid(form)

        otp.record_request(key)

        otp_code = otp.generate_otp()

        otp.store_otp(key, otp_code)
        otp.mark_resend_wait(key, seconds=30)

        self.request.session["otp_requested_at"] = phone

        print(
            f"\n==============================\n"
            f"کد بازیابی رمز برای {phone}: {otp_code}\n"
            f"==============================\n"
        )

        messages.success(
            self.request,
            "اگر شماره واردشده در سیستم وجود داشته باشد، "
            "کد تأیید در ترمینال نمایش داده شد.",
        )

        return super().form_valid(form)


class OTPVerifyView(View):
    def get(self, request):
        if "reset_phone" not in request.session:
            return redirect(
                "accounts:password_reset_request"
            )

        return render(
            request,
            "auth/password_reset_otp_verify.html",
            {"form": OTPVerifyForm()},
        )

    def post(self, request):
            phone = request.session.get("reset_phone")

            if not phone:
                return redirect("accounts:password_reset_request")

            form = OTPVerifyForm(request.POST)

            if form.is_valid():
                user_code = form.cleaned_data["code"].strip()
                key = f"reset_{phone}"
                cached_code = otp.get_otp(key)

                if otp.attempts_left(key) == 0:
                    form.add_error(
                        "code",
                        "تعداد تلاش‌های شما بیش از حد مجاز است. "
                        "لطفاً دوباره درخواست دهید.",
                    )
                elif cached_code and str(cached_code) == str(user_code):
                    otp.clear_attempts(key)
                    otp.delete_otp(key)
                    request.session["otp_verified"] = True
                    return redirect("accounts:password_reset_confirm")
                else:
                    otp.record_failed_attempt(key)
                    if not cached_code:
                        form.add_error("code", "کد منقضی شده است. لطفاً دوباره درخواست دهید.")
                    else:
                        form.add_error("code", "کد واردشده اشتباه است.")

            return render(
                request,
                "auth/password_reset_otp_verify.html",
                {"form": form},
            )



class SetNewPasswordView(View):
    def get_user(self, request):
        phone = request.session.get("reset_phone")

        if not phone:
            return None

        try:
            return User.objects.get(phone=phone)
        except User.DoesNotExist:
            return None

    def get(self, request):
        if not request.session.get("otp_verified"):
            return redirect(
                "accounts:password_reset_request"
            )

        user = self.get_user(request)

        if not user:
            return redirect(
                "accounts:password_reset_request"
            )

        form = CustomPasswordResetConfirmForm(user=user)

        return render(
            request,
            "auth/password_reset_confirm.html",
            {"form": form},
        )

    def post(self, request):
        if not request.session.get("otp_verified"):
            return redirect(
                "accounts:password_reset_request"
            )

        user = self.get_user(request)

        if not user:
            return redirect(
                "accounts:password_reset_request"
            )

        form = CustomPasswordResetConfirmForm(
            user=user,
            data=request.POST,
        )

        if form.is_valid():
            form.save()

            request.session.pop("reset_phone", None)
            request.session.pop("otp_verified", None)
            request.session.pop("sent_otp", None)

            messages.success(
                request,
                "رمز عبور شما با موفقیت تغییر کرد.",
            )

            return redirect("accounts:login")

        return render(
            request,
            "auth/password_reset_confirm.html",
            {"form": form},
        )


class CustomerViewSet(ModelViewSet):
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CustomerProfile.objects.filter(user=self.request.user)

    def get_object(self):
        from django.shortcuts import get_object_or_404

        queryset = self.filter_queryset(
            CustomerProfile.objects.filter(user=self.request.user)
        )
        return get_object_or_404(queryset, pk=self.kwargs['pk'])

    def create(self, request, *args, **kwargs):
        return Response(
            {'detail': 'استفاده از این مسیر برای ایجاد پروفایل مجاز نیست.'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    @action(detail=False, methods=["get"])
    def me(self, request):
        customer, created = CustomerProfile.objects.get_or_create(
            user=request.user
        )

        serializer = self.get_serializer(customer)

        return Response(serializer.data)


class PhoneAuthRequestView(View):
    template_name = "auth/auth_request.html"

    def get(self, request):
        return render(
            request,
            self.template_name,
        )

    def post(self, request):
        phone = request.POST.get("phone", "")
        phone = normalize_phone(phone)

        if not re.fullmatch(r"09\d{9}", phone):
            return render(
                request,
                self.template_name,
                {
                    "error": (
                        "لطفاً شماره موبایل معتبر با فرمت "
                        "09xxxxxxxxx وارد کنید."
                    ),
                    "phone": phone,
                },
            )

        if otp.is_resend_blocked(f"auth_{phone}"):
            return render(
                request,
                self.template_name,
                {
                    "error": (
                        "لطفاً کمی صبر کنید و سپس دوباره درخواست دهید."
                    ),
                    "phone": phone,
                },
            )

        if otp.too_many_requests(f"auth_{phone}"):
            return render(
                request,
                self.template_name,
                {
                    "error": (
                        "تعداد درخواست‌های شما بیش از حد مجاز است. "
                        "لطفاً بعداً دوباره تلاش کنید."
                    ),
                    "phone": phone,
                },
            )

        otp.record_request(f"auth_{phone}")

        otp_code = otp.generate_otp()

        otp.store_otp(f"auth_{phone}", otp_code)
        otp.mark_resend_wait(f"auth_{phone}", seconds=30)

        request.session["auth_phone"] = phone

        print(
            f"\n==============================\n"
            f"کد ورود برای شماره {phone}: {otp_code}\n"
            f"==============================\n"
        )

        return redirect("accounts:auth_verify")


class PhoneAuthVerifyView(View):
    template_name = "auth/auth_verify.html"

    def get(self, request):
        phone = request.session.get("auth_phone")

        if not phone:
            return redirect("accounts:auth_request")

        return render(
            request,
            self.template_name,
            {"phone": phone},
        )

    def post(self, request):
        phone = request.session.get("auth_phone")
        entered_otp = request.POST.get("otp", "").strip()

        if not phone:
            return redirect("accounts:auth_request")
        
        entered_otp = normalize_phone(entered_otp)

        key = f"auth_{phone}"

        if otp.attempts_left(key) == 0:
            return render(
                request,
                self.template_name,
                {
                    "phone": phone,
                    "error": (
                        "تعداد تلاش‌های شما بیش از حد مجاز است. "
                        "لطفاً دوباره درخواست دهید."
                    ),
                },
            )

        saved_otp = otp.get_otp(key)

        if not saved_otp:
            return render(
                request,
                self.template_name,
                {
                    "phone": phone,
                    "error": (
                        "کد ورود منقضی شده است. "
                        "لطفاً دوباره درخواست دهید."
                    ),
                },
            )

        if str(entered_otp) != str(saved_otp):
            otp.record_failed_attempt(key)
            return render(
                request,
                self.template_name,
                {
                    "phone": phone,
                    "error": "کد واردشده اشتباه است.",
                },
            )

        otp.clear_attempts(key)

        user, created = User.objects.get_or_create(
            phone=phone,
            defaults={
                "username": phone,
            },
        )

        if not user.username:
            user.username = phone
            user.save(update_fields=["username"])

        CustomerProfile.objects.get_or_create(
            user=user
        )

        login(request, user)

        otp.delete_otp(key)
        request.session.pop("auth_phone", None)

        return redirect("home")
