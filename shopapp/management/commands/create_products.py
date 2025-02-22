from django.core.management import BaseCommand
from shopapp.models import Product


class Command(BaseCommand):
    """
    Creates new products
    """
    def handle(self, *args, **options):
        product_names = ["Samsung A03", "Samsung A13", "Samsung A52", "Samsung A73"]
        for product_name in product_names:
            product, created = Product.objects.get_or_create(name=product_name)
            if created:
                self.stdout.write(self.style.SUCCESS(f"Product {product.name} successfully created"))
