from django.shortcuts import render, redirect
from . import forms


def register(request):
    if request.method == "POST":
        form = forms.RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = forms.RegisterForm()

    return render(request, 'accounts/register.html', {'form': form})
