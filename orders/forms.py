from django import forms
from accounts.models import CustomerProfile


class CheckoutForm(forms.Form):
    first_name = forms.CharField(
        max_length=150,
        label='نام',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'نام',
        }),
    )
    last_name = forms.CharField(
        max_length=150,
        label='نام خانوادگی',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'نام خانوادگی',
        }),
    )
    phone = forms.CharField(
        max_length=15,
        label='تلفن',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '09xxxxxxxxx',
            'dir': 'ltr',
        }),
    )
    city = forms.CharField(
        max_length=100,
        label='شهر',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'مثال: شیراز',
        }),
    )
    postal_code = forms.CharField(
        max_length=20,
        label='کد پستی',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'کد پستی',
            'dir': 'ltr',
        }),
    )
    address = forms.CharField(
        label='آدرس',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'آدرس دقیق پستی...',
        }),
    )

    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self._prefill(user)

    def _prefill(self, user):
        self.fields['first_name'].initial = user.first_name or ''
        self.fields['last_name'].initial = user.last_name or ''
        self.fields['phone'].initial = user.phone or ''
        try:
            profile = user.customer_profile
            self.fields['city'].initial = profile.city or ''
            self.fields['postal_code'].initial = profile.postal_code or ''
            self.fields['address'].initial = profile.address or ''
        except Exception:
            pass

    def save_profile(self, user):
        changed = False
        if self.cleaned_data.get('first_name'):
            user.first_name = self.cleaned_data['first_name']
            changed = True
        if self.cleaned_data.get('last_name'):
            user.last_name = self.cleaned_data['last_name']
            changed = True
        if changed:
            user.save(update_fields=['first_name', 'last_name'])

        profile, _ = CustomerProfile.objects.get_or_create(user=user)
        profile.city = self.cleaned_data.get('city', '') or ''
        profile.postal_code = self.cleaned_data.get('postal_code', '') or ''
        profile.address = self.cleaned_data.get('address', '') or ''
        profile.save(update_fields=['city', 'postal_code', 'address'])