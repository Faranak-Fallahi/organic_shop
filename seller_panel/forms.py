from django import forms
from store.models import Product, Category
from django import forms
from orders.models import Order 

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['title', 'image']
        labels = {
            'title': 'عنوان دسته‌بندی',
            'image': 'تصویر دسته‌بندی',
        }
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'مثال: عرقیات گیاهی'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control'
            }),
        }


class SellerProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'title',
            'category',
            'image',
            'price',
            'discount',
            'unit',
            'min_order_quantity',
            'inventory',
            'is_special',
            'is_active',
            'description',
        ]
        labels = {
            'title': 'نام محصول',
            'category': 'دسته‌بندی',
            'image': 'تصویر محصول',
            'price': 'قیمت (تومان)',
            'discount': 'درصد تخفیف',
            'unit': 'واحد فروش',
            'min_order_quantity': 'حداقل مقدار سفارش',
            'inventory': 'موجودی انبار',
            'is_special': 'قرار دادن در فروش ویژه',
            'is_active': 'وضعیت انتشار (فعال/غیرفعال)',
            'description': 'توضیحات محصول',
        }
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'مثال: آویشن کوهی اعلا'
            }),
            'category': forms.Select(attrs={
                'class': 'form-select'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'مثال: 120000',
                'min': '0'
            }),
            'discount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'از 0 تا 100',
                'min': '0',
                'max': '100'
            }),
            'unit': forms.Select(attrs={
                'class': 'form-select'
            }),
            'min_order_quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'مثال: 100',
                'min': '1'
            }),
            'inventory': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'مثال: 50',
                'min': '0'
            }),
            'is_special': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'خواص، نحوه مصرف یا توضیحات کامل محصول...'
            }),
        }

class OrderStatusUpdateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['status'] 
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select', 'style': 'border-radius: 8px;'}),
        }
        labels = {
            'status': 'وضعیت سفارش',
        }

    def clean(self):
        cleaned = super().clean()
        status = cleaned.get('status')
        if (
            self.instance is not None
            and self.instance.status == Order.ORDER_STATUS_CANCELED
            and status is not None
            and status != Order.ORDER_STATUS_CANCELED
        ):
            raise forms.ValidationError('سفارش لغوشده قابل بازگرداندن نیست.')
        return cleaned
