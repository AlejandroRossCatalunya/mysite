from django.urls import path, include
from django.views.decorators.cache import cache_page
from rest_framework.routers import DefaultRouter
from .views import (ShopIndex,
                    GroupsList,
                    LatestProductsFeed,
                    ProductViewSet,
                    ProductsListView,
                    ProductDetailsView,
                    ProductCreateView,
                    ProductUpdateView,
                    ProductDeleteView,
                    ProductsDataExportView,
                    OrderViewSet,
                    OrdersListView,
                    OrderDetailsView,
                    OrderCreateView,
                    OrderUpdateView,
                    OrderDeleteView,
                    OrdersExportView,
                    UserOrdersListView,
                    UserOrdersExportView)

app_name = "shopapp"

routers = DefaultRouter()
routers.register("products", ProductViewSet)
routers.register("orders", OrderViewSet)
routers.register("users", UserOrdersExportView, "orders")

urlpatterns = [
    #path("", cache_page(180)(ShopIndex.as_view()), name="index"),
    path("", ShopIndex.as_view(), name="index"),
    path("api/", include(routers.urls)),
    path("groups/", GroupsList.as_view(), name="groups_list"),
    path("products/", ProductsListView.as_view(), name="products_list"),
    path("products/<int:pk>/", ProductDetailsView.as_view(), name="product_details"),
    path("products/<int:pk>/update", ProductUpdateView.as_view(), name="product_update"),
    path("products/<int:pk>/archived", ProductDeleteView.as_view(), name="product_delete"),
    path("products/create/", ProductCreateView.as_view(), name="product_create"),
    path("products/export", ProductsDataExportView.as_view(), name="products-export"),
    path("products/latest/feed/", LatestProductsFeed(), name="products-feed"),
    path("orders/", OrdersListView.as_view(), name="orders_list"),
    path("orders/<int:pk>/", OrderDetailsView.as_view(), name="order_details"),
    path("orders/create/", OrderCreateView.as_view(), name="order_create"),
    path("orders/<int:pk>/update", OrderUpdateView.as_view(), name="order_update"),
    path("orders/<int:pk>/delete", OrderDeleteView.as_view(), name="order_delete"),
    path("orders/export", OrdersExportView.as_view(), name="orders-export"),
    path("users/<int:user_id>/orders/", UserOrdersListView.as_view(), name="user_orders")
]