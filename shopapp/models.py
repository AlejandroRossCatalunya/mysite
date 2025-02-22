from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.db import models
from django.urls import reverse

def product_preview_directory_path(instance: "Product", filename: str) -> str:
    return "products/product_{pk}/preview/{filename}".format(
        pk=instance.pk,
        filename=filename
    )


class Product(models.Model):
    """
    Модель Product представляет товар,
    который можно продавать в интернет-магазине.

    Заказы тут: :model:`shopapp.Order`
    """
    class Meta:
        ordering = ["name", "price"]
        verbose_name = _("Product")
        verbose_name_plural = _("Products")
    name = models.CharField(max_length=100, db_index=True)
    color = models.CharField(max_length=40, db_index=True)
    description = models.TextField(null=False, blank=True)
    price = models.DecimalField(default=10000, max_digits=6, decimal_places=0)
    discount = models.PositiveSmallIntegerField(default=0)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="products")
    created_at = models.DateTimeField(auto_now_add=True)
    archived = models.BooleanField(default=False)
    preview = models.ImageField(null=True, blank=True, upload_to=product_preview_directory_path)

    def get_absolute_url(self):
        return reverse("shopapp:product_details", kwargs={"pk": self.pk})


    # @property
    # def description_short(self):
    #     if len(self.description) < 48:
    #         return self.description
    #     return self.description[:48] + "..."

    def __str__(self):
        return f"Product ({self.name!r}, color: {self.color})"

def product_images_directory_path(instance: "ProductImage", filename: str) -> str:
    return "products/product_{pk}/images/{filename}".format(
        pk=instance.product.pk,
        filename=filename
    )


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to=product_images_directory_path)
    description = models.CharField(max_length=200, null=False, blank=True)


class Order(models.Model):
    class Meta:
        verbose_name = _("Order")
        verbose_name_plural = _("Orders")
    delivery_address = models.TextField(null=False, blank=True)
    promocode = models.CharField(max_length=25)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="orders")
    products = models.ManyToManyField(Product, related_name="orders")
    receipt = models.FileField(null=True, upload_to='orders/receipts/')
