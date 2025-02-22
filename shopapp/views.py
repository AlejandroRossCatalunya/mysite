"""
В этом модуле лежат различные наборы представлений.

Разные view интернет-магазина: по товарам, заказам и т. д.
"""
import logging
import json
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from django.http import HttpResponse, HttpResponseRedirect, HttpRequest, JsonResponse
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.core.cache import cache
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.generic import View, ListView, DetailView, CreateView, UpdateView, DeleteView
from django.utils.translation import gettext_lazy as _, ngettext
from drf_spectacular.utils import extend_schema, OpenApiResponse
from .models import Product, Order, ProductImage
from .forms import ProductForm, OrderForm, GroupForm
from .serializers import ProductSerializer, OrderSerializer
from .common import save_csv_products
from django.contrib.auth.models import User, Group
from django.contrib.syndication.views import Feed
from timeit import default_timer
from csv import DictWriter


#log = logging.getLogger(__name__)


class LatestProductsFeed(Feed):
    title = "Products (latest)"
    description = "Updates on changes and addition products"
    link = reverse_lazy("shopapp:products_list")

    def items(self):
        return Product.objects.filter(created_at__isnull=False).order_by("-created_at")[:5]

    def item_title(self, item: Product):
        return item.name

    def item_description(self, item: Product):
        return item.description[:100]

    def item_link(self, item: Product):
        return item.get_absolute_url()


@extend_schema(description="Product views CRUD")
class ProductViewSet(ModelViewSet):
    """
    Набор представлений для действий над Product
    Полный CRUD для сущностей товара
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [
        SearchFilter,
        OrderingFilter
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
        "discount"
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

    @method_decorator(cache_page(120))
    def list(self, *args, **kwargs):
        return super().list(*args, **kwargs)

    @action(methods=["get"], detail=False)
    def download_csv(self, request: Request):
        response = HttpResponse(content_type="text/csv")
        filename = "products-export.csv"
        response["Content-Disposition"] = f"attachment; filename={filename}"
        queryset = self.filter_queryset(self.get_queryset())
        fields = [
            "name",
            "description",
            "price",
            "discount"
        ]
        queryset = queryset.only(*fields)
        writer = DictWriter(response, fieldnames=fields)
        writer.writeheader()
        for product in queryset:
            writer.writerow({field: getattr(product, field) for field in fields})
        return response

    @action(methods=["post"], detail=False, parser_classes=[MultiPartParser])
    def upload_csv(self, request: Request):
        products = save_csv_products(
            request.FILES["file"].file,
            encoding="UTF-8"
        )
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)


class OrderViewSet(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    filter_backends = [
        DjangoFilterBackend,
        OrderingFilter
    ]
    search_fields = ["delivery_address", "user"]
    filterset_fields = [
        "delivery_address",
        "promocode",
        "created_at",
        "user"
    ]
    ordering_fields = [
        "delivery_address",
        "user"
    ]


class ShopIndex(View):
    #@method_decorator(cache_page(120))
    def get(self, request):
        products = [
            {"name": "Samsung A03", "price": 8990, "color": "black", "qty": 5},
            {"name": "Samsung A13", "price": 15990, "color": "blue", "qty": 7},
            {"name": "Samsung A52", "price": 30990, "color": "red", "qty": 8},
            {"name": "Samsung A73", "price": 41990, "color": "blue", "qty": 2}
        ]
        context = {
            "time_running": default_timer(),
            "products": products,
            "items": 5,
            "header": "Welcome to Samsung GALAXY store",
            "title": "Samsung GALAXY Store"
        }
        #log.debug("Products for shop index: %s", products)
        #log.info("Rendering shop index")
        print("shop index context", context)
        return render(request, "shopapp/shop-index.html", context=context)


class GroupsList(View):
    def get(self, request):
        context = {
            "title": "Groups list",
            "form": GroupForm(),
            "groups": Group.objects.prefetch_related("permissions").all()
        }
        return render(request, "shopapp/groups-list.html", context=context)

    def post(self, request):
        form = GroupForm(request.POST)
        if form.is_valid():
            form.save()
        return redirect(request.path)


class ProductDetailsView(DetailView):
    template_name = "shopapp/products-details.html"
    #model = Product
    queryset = Product.objects.prefetch_related("images")
    context_object_name = "product"


class ProductsListView(LoginRequiredMixin, ListView):
    login_url = reverse_lazy("myauth:login")
    template_name = "shopapp/products-list.html"
    queryset = Product.objects.filter(archived=False)
    context_object_name = "products"


class ProductCreateView(PermissionRequiredMixin, CreateView):
    permission_required = "shopapp.add_product"
    template_name = "shopapp/create-product.html"
    form_class = ProductForm
    model = Product
    #fields = "name", "color", "description", "price", "discount", "preview"
    success_url = reverse_lazy("shopapp:products_list")

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class ProductUpdateView(UserPassesTestMixin, UpdateView):
    model = Product
    #fields = "name", "color", "description", "price", "discount", "preview"
    template_name_suffix = "_update_form"
    form_class = ProductForm

    def test_func(self):
        if self.request.user.is_superuser:
            return True

        self.object = self.get_object()

        has_edit_perm = self.request.user.has_perm("shopapp.change_product")
        created_by_current_user = self.object.created_by == self.request.user
        return has_edit_perm and created_by_current_user

    def get_success_url(self):
        return reverse(
            "shopapp:product_details",
            kwargs={"pk": self.object.pk}
        )

    def form_valid(self, form):
        response = super().form_valid(form)
        for image in form.files.getlist("images"):
            ProductImage.objects.create(
                product=self.object,
                image=image
            )
        return response


class ProductDeleteView(DeleteView):
    model = Product
    success_url = reverse_lazy("shopapp:products_list")

    def form_valid(self, form):
        success_url = self.get_success_url()
        self.object.archived = True
        self.object.save()
        return HttpResponseRedirect(success_url)


class ProductsDataExportView(View):
    def get(self, request: HttpRequest) -> JsonResponse:
        cache_key = "products_data_export"
        products_data = cache.get(cache_key)
        if products_data is None:
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
            cache.set(cache_key, products_data, 300)
        return JsonResponse({"products": products_data})


# class ProductsListView(TemplateView):
#     template_name = "shopapp/products-list.html"
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context["products"] = Product.objects.all()
#         return context


# def products_list(request):
#     context = {
#         "title": "Products list",
#         "products": Product.objects.all()
#     }
#     return render(request, "shopapp/products-list.html", context=context)


# def create_product(request):
#     if request.method == "POST":
#         form = ProductForm(request.POST)
#         if form.is_valid():
#             # Product.objects.create(**form.cleaned_data)
#             form.save()
#             return redirect(reverse("shopapp:products_list"))
#     else:
#         form = ProductForm()
#     context = {"form": form}
#     return render(request, "shopapp/create-product.html", context=context)


class OrdersListView(LoginRequiredMixin, ListView):
    queryset = (Order.objects.select_related("user").prefetch_related("products"))


class OrderDetailsView(PermissionRequiredMixin, DetailView):
    permission_required = "shopapp.view_order"
    queryset = (Order.objects.select_related("user").prefetch_related("products"))


class OrderCreateView(CreateView):
    model = Order
    fields = "user", "delivery_address", "promocode", "products"
    success_url = reverse_lazy("shopapp:orders_list")


class OrderUpdateView(UpdateView):
    model = Order
    fields = "user", "delivery_address", "promocode", "products"
    template_name_suffix = "_update"

    def get_success_url(self):
        return reverse(
            "shopapp:order_details",
            kwargs={"pk": self.object.pk}
        )


class OrderDeleteView(DeleteView):
    queryset = (Order.objects.select_related("user").prefetch_related("products"))
    success_url = reverse_lazy("shopapp:orders_list")

# def orders_list(request):
#     context = {
#         "title": "Orders list",
#         "orders": Order.objects.select_related("user").prefetch_related("products").all()
#     }
#     return render(request, "shopapp/orders-list.html", context=context)


# def create_order(request):
#     if request.method == "POST":
#         form = OrderForm(request.POST)
#         if form.is_valid():
#             # Order.objects.create(**form.cleaned_data)
#             # user = form.cleaned_data.get("user")
#             # delivery_address = form.cleaned_data.get("delivery_address")
#             # promo = form.cleaned_data.get("promocode")
#             # products = form.cleaned_data.get("products")
#             # instance = Order.objects.create(delivery_address=delivery_address,
#             #                                 promocode=promo,
#             #                                 created_at=datetime.now(),
#             #                                 user=user)
#             # instance.products.set(products)
#             form.save()
#             return redirect(reverse("shopapp:orders_list"))
#     else:
#         form = OrderForm()
#     context = {"form": form, "products": Product.objects.all()}
#     return render(request, "shopapp/create-order.html", context=context)

class OrdersExportView(UserPassesTestMixin, View):
    def test_func(self):
        if self.request.user.is_staff:
            return True

    def get(self, request: HttpRequest) -> JsonResponse:
        orders = Order.objects.order_by("pk").all()
        orders_data = [
            {
                "pk": order.pk,
                "delivery_address": order.delivery_address,
                "promocode": order.promocode,
                "user_id": order.user.pk,
                "products_id": sorted([p.pk for p in order.products.all()])
            }
            for order in orders
        ]
        return JsonResponse({"orders": orders_data})


class UserOrdersListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = "shopapp/user_orders.html"

    def get_queryset(self):
        self.owner = get_object_or_404(User, id=self.kwargs["user_id"])
        queryset = Order.objects.select_related("user").prefetch_related("products").filter(user__id=self.kwargs["user_id"])
        return queryset

    def get_context_data(self, order_list=None, *args, **kwargs):
        data = super().get_context_data(object_list=order_list, **kwargs)
        data["owner"] = self.owner
        return data


class UserOrdersExportView(LoginRequiredMixin, ModelViewSet):
    serializer_class = OrderSerializer
    filter_backends = [
        SearchFilter,
        OrderingFilter
    ]
    search_fields = ["delivery_address"]
    filterset_fields = [
        "delivery_address",
        "promocode",
        "created_at",
        "products"
    ]
    ordering_fields = ["id"]

    def get_queryset(self):
        queryset = Order\
            .objects.select_related("user")\
            .prefetch_related("products")\
            .filter(user__id=self.kwargs['pk'])\
            .order_by("pk")
        return queryset

    def get_user(self, pk):
        return get_object_or_404(User, id=pk)

    @action(methods=["get"], detail=True)
    def orders(self, request: Request, pk=None):
        self.owner = self.get_user(pk)
        cache_key = f"{self.owner.username}{self.owner.email}_orders_export"
        user_orders_data = cache.get(cache_key)
        if user_orders_data is None:
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.serializer_class(queryset, many=True)
            user_orders_data = serializer.data
            cache.set(cache_key, user_orders_data, 300)
        return Response(user_orders_data)

    @action(methods=["get"], detail=True)
    def order_export(self, request: Request, pk=None):
        self.owner = self.get_user(pk)
        filename = f"{self.owner.username} orders export.json"
        cache_key = f"{self.owner.username}{self.owner.email}_orders_export"
        user_orders_data = cache.get(cache_key)
        if user_orders_data is None:
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.serializer_class(queryset, many=True)
            user_orders_data = serializer.data
            cache.set(cache_key, user_orders_data, 300)
        return HttpResponse(
            content=user_orders_data,
            content_type="application/force-download",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )

