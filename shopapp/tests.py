from datetime import datetime

from django.contrib.auth.models import User, Permission
from django.test import TestCase
from django.urls import reverse
from string import ascii_letters
from random import choices
from django.conf import settings

from shopapp.models import Product, Order


class ProductCreateViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.user = User.objects.create_user(username="testuser", password="testpswd")
        cls.user.user_permissions.add(Permission.objects.get(codename="add_product"))

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()

    def setUp(self) -> None:
        self.client.force_login(self.user)
        self.product_name = "".join(choices(ascii_letters, k=10))
        Product.objects.filter(name=self.product_name).delete()

    def test_create_product(self) -> None:
        response = self.client.post(reverse("shopapp:product_create"),
                                    {
                                        "name": self.product_name,
                                        "color": "blue",
                                        "description": "Test description for product",
                                        "price": 40000,
                                        "discount": 25
                                    },
                                    HTTP_USER_AGENT="Test")
        self.assertRedirects(response, reverse("shopapp:products_list"))
        self.assertTrue(Product.objects.filter(name=self.product_name).exists())


class ProductDetailsViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.user = User.objects.create_user(username="testuser", password="testpswd")
        cls.product = Product.objects.create(name="Best Product", created_by=User.objects.get(id=cls.user.id))

    @classmethod
    def tearDownClass(cls):
        cls.product.delete()
        cls.user.delete()

    def test_get_product(self):
        response = self.client.get(
            reverse("shopapp:product_details", kwargs={"pk": self.product.pk}),
            HTTP_USER_AGENT="Test"
        )
        self.assertEqual(response.status_code, 200)

    def test_get_product_and_check_content(self):
        response = self.client.get(
            reverse("shopapp:product_details", kwargs={"pk": self.product.pk}),
            HTTP_USER_AGENT="Test"
        )
        self.assertContains(response, self.product.name)


class ProductsListViewTestCase(TestCase):
    fixtures = ["products-fixture.json", "users.json"]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="testuser", password="testpswd")

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()

    def setUp(self) -> None:
        self.client.force_login(self.user)

    def test_products_list_view(self):
        response = self.client.get(reverse("shopapp:products_list"), HTTP_USER_AGENT="Test")
        self.assertQuerysetEqual(
            qs=Product.objects.filter(archived=False).all(),
            values=(p.pk for p in response.context["products"]),
            transform=lambda p: p.pk
        )
        self.assertTemplateUsed(response, "shopapp/products-list.html")


class OrdersListViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="testuser", password="testpswd")

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()

    def setUp(self) -> None:
        self.client.force_login(self.user)

    def test_orders_view(self):
        response = self.client.get(reverse("shopapp:orders_list"), HTTP_USER_AGENT="Test")
        self.assertContains(response, "Orders")

    def test_orders_view_not_authenticated(self):
        self.client.logout()
        response = self.client.get(reverse("shopapp:orders_list"), HTTP_USER_AGENT="Test")
        self.assertEqual(response.status_code, 302)
        self.assertIn(str(settings.LOGIN_URL), response.url)


class ProductsExportViewTestCase(TestCase):
    fixtures = ["products-fixture.json", "users.json"]

    def test_get_products_view(self):
        response = self.client.get(reverse("shopapp:products-export"), HTTP_USER_AGENT="Test")
        self.assertEqual(response.status_code, 200)
        products = Product.objects.order_by("pk").all()
        expected_data = [
            {
                "pk": product.pk,
                "name": product.name,
                "price": str(product.price),
                "archived": product.archived
            }
            for product in products
        ]
        products_data = response.json()
        self.assertEqual(products_data["products"], expected_data)


class OrderDetailViewTestCase(TestCase):
    fixtures = ["order.json", "product.json", "users.json"]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="testuser", password="testpswd")
        cls.user.user_permissions.add(Permission.objects.get(codename="view_order"))

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()

    def setUp(self) -> None:
        self.client.force_login(self.user)
        self.order = Order.objects.create(delivery_address="Nevskiy av., 4",
                                          promocode="SALESPB",
                                          created_at=datetime.now(),
                                          user=self.user)
        self.order.products.set(Product.objects.filter(archived=False).all())
    def tearDown(self) -> None:
        self.order.delete()

    def test_order_details(self):
        print(Product.objects.filter(archived=False).all())
        response = self.client.get(reverse("shopapp:order_details", kwargs={"pk": self.order.pk}),
                                   HTTP_USER_AGENT="Test")
        self.assertContains(response, self.order.delivery_address)
        self.assertContains(response, self.order.promocode)
        self.assertEqual(response.context["order"].pk, self.order.pk)


class OrdersExportTestCase(TestCase):
    fixtures = ["order.json", "product.json", "users.json"]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="testuser", password="testpswd", is_staff=True)

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()

    def setUp(self) -> None:
        self.client.force_login(self.user)

    def test_get_products_view(self):
        response = self.client.get(reverse("shopapp:orders-export"), HTTP_USER_AGENT="Test")
        self.assertEqual(response.status_code, 200)
        orders = Order.objects.order_by("pk").all()
        expected_data = [
            {
                "pk": order.pk,
                "delivery_address": order.delivery_address,
                "promocode": order.promocode,
                "user_id": order.user.pk,
                "products_id": sorted([p.pk for p in order.products.all()])
            }
            for order in orders
        ]
        orders_data = response.json()
        self.assertEqual(orders_data["orders"], expected_data)
