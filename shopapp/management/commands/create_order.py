from django.core.management import BaseCommand
from django.db import transaction
from shopapp.models import Order, Product
from django.contrib.auth.models import User
from typing import Sequence


class Command(BaseCommand):
    """
    Creates new orders
    """
    @transaction.atomic
    def handle(self, *args, **options):
        user = User.objects.get(username="admin")
        products: Sequence[Product] = Product.objects.defer("description", "price", "created_at").all()
        # products: Sequence[Product] = Product.objects.only("id").all()
        order = Order.objects.get_or_create(
            delivery_address="SPb, Nevskiy av.",
            promocode = "SALESPB",
            user=user
        )
        self.stdout.write(f"Order {order} successfully created")
