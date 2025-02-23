from django.urls import path

from .views import shop_index, groups_list, products_list, orders_list, create_product, order_create, order_created

app_name = "shopapp"
urlpatterns = [
    path("", shop_index, name="index"),
    path("groups/", groups_list, name="groups_list"),
    path("products/", products_list, name="products_list"),
    path("product/create/", create_product, name="product_create"),
    path("orders/", orders_list, name="orders_list"),
    path('order/create/', order_create, name='order_create'),
    path('order/created/<int:order_id>/', order_created, name='order_created'),

]