from django.shortcuts import render, redirect
from . import forms
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordChangeView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy





def register(request):
    if request.method == "POST":
        form = forms.RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
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