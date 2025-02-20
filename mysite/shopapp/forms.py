from django import forms
from .models import Product, Order


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'price', 'description', 'discount']  # Используйте список

    def clean_price(self):
        price = self.cleaned_data['price']
        if price < 0:
            raise forms.ValidationError("Цена не может быть отрицательной.")
        return price

    def clean_discount(self):
        discount = self.cleaned_data['discount']
        if discount < 0:
            raise forms.ValidationError("Скидка не может быть отрицательной.")
        return discount


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['delivery_address', 'promocode', 'products']

    def clean_promocode(self):
        promocode = self.cleaned_data.get('promocode')
        if not promocode:
            raise forms.ValidationError("Промокод не может быть пустым.")
        return promocode

    def clean_products(self):
        products = self.cleaned_data.get('products')
        if not products:
            raise forms.ValidationError("Выберите хотя бы один продукт.")
        return products
