from django.shortcuts import render, redirect
from . import forms
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required



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