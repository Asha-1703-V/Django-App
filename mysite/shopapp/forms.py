from django.forms import ModelForm, forms, CheckboxSelectMultiple, formset_factory
from django.contrib.auth.models import Group
from .models import Order, ProductImage
from django import forms
from shopapp.models import Product

class OrderImportForm(forms.Form):
    file = forms.FileField()

class ProductForm(forms.ModelForm):
    images = forms.FileField(
        required=False
    )

    class Meta:
        model = Product
        fields = ('name', 'price', 'description', 'discount', 'preview')

class ProductImageForm(forms.ModelForm):
    image = forms.FileField(
        required=False
    )

    class Meta:
        model = ProductImage
        fields = ('image',)

ProductImageFormSet = forms.formset_factory(ProductImageForm, extra=5)


class GroupForm(ModelForm):
    class Meta:
        model = Group
        fields = ["name"]

class OrderForm(ModelForm):
    class Meta:
        model = Order
        fields = ("delivery_address", "promocode", "user", "products")
        widgets = {
            'products': CheckboxSelectMultiple(),
        }


class CSVImportForm(forms.Form):
    csv_file =  forms.FileField()