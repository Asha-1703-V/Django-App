"""
В этом модуле лежат различные наборы представлений.

Разные view интернет-магазина: по товарам, заказам и т.д.
"""

import logging
from timeit import default_timer

from django.contrib.auth.models import Group
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect, reverse
from django.urls import reverse_lazy
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from drf_spectacular.utils import extend_schema, OpenApiResponse

from .forms import GroupForm, OrderForm
from .forms import ProductForm, ProductImageFormSet
from .models import Product, Order, ProductImage
from .serializers import ProductSerializer, OrderSerializer

log = logging.getLogger(__name__)

@extend_schema(description="Product views CRUD")
class ProductViewSet(ModelViewSet):
    """
    Набор представлений для действий над Product.

    Полный CRUD для сущностей товара.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [
        SearchFilter,
        DjangoFilterBackend,
        OrderingFilter,
    ]
    search_fields = ["name", "description"]
    filterset_fields = [
        "name",
        "description",
        "price",
        "discount",
        "archived"
    ]
    ordering_fields = [
        "name",
        "price",
        "discount",
    ]

    @extend_schema(
        summary="Get one product by ID",
        description="Retrieves **product**, returns 404 if not found",
        responses={
            200: ProductSerializer,
            404: OpenApiResponse(description="Empty response, product by id not found"),
        }
    )
    def retrieve(self, *args, **kwargs):
        return super().retrieve(*args, **kwargs)

class OrderViewSet(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    filter_backends = [
        DjangoFilterBackend,
        OrderingFilter
    ]
    filterset_fields = [
        "user",
        "delivery_address",
        "promocode",
    ]
    ordering_fields = [
        "id",
        "user",
    ]

class OrdersExportView(UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.is_staff

    def get(self, request):
        orders = Order.objects.select_related("user").prefetch_related("products")
        orders_data = [
            {
                "id": order.pk,
                "delivery_address": order.delivery_address,
                "promocode": order.promocode,
                "user_id": order.user.pk,
                "product_ids": [product.pk for product in order.products.all()],
            }
            for order in orders
        ]
        return JsonResponse({"orders": orders_data})

class ProductCreateView(CreateView):
    model = Product
    form_class = ProductForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['image_formset'] = ProductImageFormSet()
        return context

    def form_valid(self, form):
        self.object = form.save()

        # Обработка множественных изображений
        image_formset = ProductImageFormSet(self.request.POST, self.request.FILES)
        if image_formset.is_valid():
            for image_form in image_formset:
                if image_form.cleaned_data:
                    ProductImage.objects.create(
                        product=self.object,
                        image=image_form.cleaned_data['image']
                    )

        return redirect(self.success_url)


class ProductUpdateView(PermissionRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Product
    form_class = ProductForm
    permission_required = "shop.change_product"
    success_url = "/ru/shop/products/"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['image_formset'] = ProductImageFormSet()
        return context

    def form_valid(self, form):
        self.object = form.save()

        # Обработка множественных изображений
        image_formset = ProductImageFormSet(self.request.FILES)
        if image_formset.is_valid():
            for image_form in image_formset:
                if image_form.cleaned_data:
                    ProductImage.objects.create(
                        product=self.object,
                        image=image_form.cleaned_data['image']
                    )

        return redirect(self.success_url)

    def test_func(self):
        return self.request.user.is_superuser or self.request.user.is_staff


class ShopIndexView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        products = [
            ('Laptop', 1999),
            ('Desktop', 2999),
            ('Smartphone', 999)
        ]
        context = {
            "time_running": default_timer(),
            "products": products,
            "items": 5,
        }
        log.debug("Products for shop index: %s", products)
        log.info("Rendering shop index")
        return render(request, 'shopapp/shop-index.html', context=context)

class GroupsListView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        context = {
            "form": GroupForm(),
            "groups": Group.objects.prefetch_related('permissions').all(),
        }
        return render(request, 'shopapp/groups-list.html', context=context)

    def post(self, request: HttpRequest):
        form = GroupForm(request.POST)
        if form.is_valid():
            form.save()

        return redirect(request.path)

class ProductDetailsView(DetailView):
    template_name = "shopapp/products-details.html"
    # model = Product
    queryset = Product.objects.prefetch_related("images")
    context_object_name = "product"

    def get_queryset(self):
        return Product.objects.filter(archived=False)

class ProductsListView(ListView):
    template_name = "shopapp/products-list.html"
    context_object_name = "products"
    queryset = Product.objects.filter(archived=False)

class ProductDeleteView(DeleteView):
    model = Product
    success_url = reverse_lazy("shopapp:products_list")

    def form_valid(self, form):
        success_url = self.get_success_url()
        self.object.archived = True
        self.object.save()
        return HttpResponseRedirect(success_url)


class OrdersListView(LoginRequiredMixin, ListView):
    queryset = (
        Order.objects
        .select_related("user")
        .prefetch_related("products")
        .all()
    )
    template_name = "shopapp/orders_list.html"
    context_object_name = "orders"

class OrderDetailView(PermissionRequiredMixin, DetailView):
    permission_required = "shopapp.view_order"
    queryset = (
        Order.objects
        .select_related("user")
        .prefetch_related("products")
    )
    template_name = "shopapp/order_detail.html"
    context_object_name = "order"

class OrderCreateView(CreateView):
    model = Order
    form_class = OrderForm
    success_url = reverse_lazy("shopapp:orders_list")

    def get_form(self, *args, **kwargs):
        form = super().get_form(*args, **kwargs)
        form.fields['products'].queryset = Product.objects.filter(archived=False)
        return form

class OrderUpdateView(UpdateView):
    model = Order
    form_class = OrderForm
    template_name_suffix = "_update_form"

    def get_success_url(self):
        return reverse("shopapp:order_details", kwargs={"pk": self.object.pk})

class OrderDeleteView(DeleteView):
    model = Order
    template_name = "shopapp/order_confirm_delete.html"
    success_url = reverse_lazy("shopapp:orders_list")

class ProductsDataExportView(View):
    def get(self, request: HttpResponse) -> JsonResponse:
        products = Product.objects.order_by("pk").all()
        products_data = [
            {
                "pk": product.pk,
                "name": product.name,
                "price": product.price,
                "archived": product.archived
            }
            for product in products
        ]
        elem = products_data[0]
        name = elem["name"]
        print("name:", name)
        return JsonResponse({"products": products_data})