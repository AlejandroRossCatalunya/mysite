from django.core.management import BaseCommand
from django.db.models import Avg, Max, Min, Count, Sum
from shopapp.models import Product, Order
from django.contrib.auth.models import User
#from typing import Sequence


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.stdout.write("Start demo aggregate")
        result = Product.objects.aggregate(
            Avg("price"),
            Max("price"),
            min_price=Min("price"),
            count=Count("id")
        )
        print(result)
        orders = Order.objects.annotate(
            total=Sum("products__price", default=0),
            products_count=Count("products")
        )
        for order in orders:
            print(f"Order #{order.id} with {order.products_count} products worth {order.total}")
        self.stdout.write("Done")
