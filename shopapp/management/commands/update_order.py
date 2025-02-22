from django.core.management import BaseCommand
from shopapp.models import Order, Product
from django.contrib.auth.models import User


class Command(BaseCommand):
    """
    Updates current order
    """
    def handle(self, *args, **options):
        order = Order.objects.first()
        if not order:
            self.stdout.write("No order found")
            return
        products = Product.objects.all()
        for product in products:
            order.products.add(product)
        self.stdout.write(f"Successfully added products {order.products.all()} to order {order}")