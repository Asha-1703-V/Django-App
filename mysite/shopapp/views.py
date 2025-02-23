from timeit import default_timer

from django.contrib.auth.models import Group
from django.http import HttpResponse, HttpRequest
from django.shortcuts import render, redirect, reverse, get_object_or_404

from .forms import OrderForm
from .forms import ProductForm
from .models import Product, Order


def shop_index(request: HttpRequest):
    products = [
        ('Laptop', 1999),
        ('Desktop', 2999),
        ('Smartphone', 999)
    ]
    context = {
        "time_running": default_timer(),
        "products": products,

    }
    return render(request, 'shopapp/shop-index.html', context=context)

def groups_list(request: HttpRequest):
    context = {
        "groups": Group.objects.prefetch_related('permissions').all(),
    }
    return render(request, 'shopapp/groups-list.html', context=context)

def products_list(request: HttpRequest):
    context = {
        "products": Product.objects.all(),
    }
    return render(request, 'shopapp/products-list.html', context=context)

def create_product(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = ProductForm(request.POST)
        if form.is_valid():
            # name = form.cleaned_data["name"]
            # Product.objects.create(**form.cleaned_data)
            form.save()
            url = reverse("shopapp:products_list")
            return redirect(url)
    else:
        form = ProductForm()
    context = {
        "form": form,
    }
    return render(request, 'shopapp/create-product.html', context=context)

def orders_list(request: HttpRequest):
    context = {
        "orders": Order.objects.select_related("user").prefetch_related("products").all(),
    }
    return render(request, 'shopapp/orders-list.html', context=context)


from timeit import default_timer

from django.contrib.auth.models import Group
from django.http import HttpResponse, HttpRequest
from django.shortcuts import render, redirect, reverse, get_object_or_404

from .forms import OrderForm
from .forms import ProductForm
from .models import Product, Order


def shop_index(request: HttpRequest):
    products = [
        ('Laptop', 1999),
        ('Desktop', 2999),
        ('Smartphone', 999)
    ]
    context = {
        "time_running": default_timer(),
        "products": products,

    }
    return render(request, 'shopapp/shop-index.html', context=context)

def groups_list(request: HttpRequest):
    context = {
        "groups": Group.objects.prefetch_related('permissions').all(),
    }
    return render(request, 'shopapp/groups-list.html', context=context)

def products_list(request: HttpRequest):
    context = {
        "products": Product.objects.all(),
    }
    return render(request, 'shopapp/products-list.html', context=context)

def create_product(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = ProductForm(request.POST)
        if form.is_valid():
            # name = form.cleaned_data["name"]
            # Product.objects.create(**form.cleaned_data)
            form.save()
            url = reverse("shopapp:products_list")
            return redirect(url)
    else:
        form = ProductForm()
    context = {
        "form": form,
    }
    return render(request, 'shopapp/create-product.html', context=context)

def orders_list(request: HttpRequest):
    context = {
        "orders": Order.objects.select_related("user").prefetch_related("products").all(),
    }
    return render(request, 'shopapp/orders-list.html', context=context)


def order_create(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)  # Не сохраняем сразу
            order.user = request.user  # Устанавливаем текущего пользователя
            order.save()  # Сохраняем заказ в базе данных
            return redirect('shopapp:order_created', order_id=order.id)  # Перенаправление на страницу подтверждения
    else:
        form = OrderForm()

    context = {
        'form': form,
    }
    return render(request, 'shopapp/create-order.html', context=context)

def order_created(request: HttpRequest, order_id: int) -> HttpResponse:
    order = get_object_or_404(Order, id=order_id)
    context = {
        'order': order,
    }
    return render(request, 'shopapp/order-created.html', context=context)