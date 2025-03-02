from django.forms import ModelForm, forms, CheckboxSelectMultiple
from django.contrib.auth.models import Group
from .models import Order
from django import forms
from shopapp.models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = 'name', 'price', 'description', 'discount', "preview"

    images = forms.ImageField(
        widget=forms.ClearableFileInput(attrs={"multiple": True}),
    )

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