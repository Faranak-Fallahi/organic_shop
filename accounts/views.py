from django.shortcuts import render, redirect
from . import forms
from django.contrib.auth.views import LoginView



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
