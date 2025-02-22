from django.core.management import BaseCommand
from django.db import transaction
from shopapp.models import Product
from django.contrib.auth.models import User
#from typing import Sequence


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.stdout.write("Start demo bulk actions")

        info = [
            ("S1", 100),
            ("S2", 200),
            ("S3", 300)
        ]
        products = [
            Product(name=name, price=price)
            for name, price in info
        ]
        result = Product.objects.bulk_create(products)
        for obj in result:
            print(obj)

        result = Product.objects.filter(name_contains="S").update(discount=10)
        print(result)

        self.stdout.write("Done")
