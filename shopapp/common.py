from io import TextIOWrapper
from csv import DictReader
from json import loads
from django.contrib.auth.models import User

from .models import Product, Order


def save_csv_products(file, encoding="UTF-8"):
    csv_file = TextIOWrapper(file, encoding)
    reader = DictReader(csv_file)
    products = [Product(**row) for row in reader]
    for product in products:
        product.created_by = request.user
    Product.objects.bulk_create(products)
    return products


def save_csv_orders(file, encoding="UTF-8"):
    csv_file = TextIOWrapper(file, encoding)
    reader = DictReader(csv_file)
    raw_orders = [
        {"delivery_address": row["delivery_address"],
        "promocode": row["promocode"],
        "user": row["user"],
        "products": row["products"]}
        for row in reader
        ]
    orders = []
    for i in range(len(raw_orders)):
        if raw_orders[i]["products"][0] == '(':
            raw_orders[i]["products"] = tuple(map(int, raw_orders[i]["products"][1:-1].split(',')))
        else:
            raw_orders[i]["products"] = (int(raw_orders[i]["products"]),)
        current_user = User.objects.get(username=raw_orders[i]["user"])
        current_order = Order(
            delivery_address=raw_orders[i]["delivery_address"],
            promocode=raw_orders[i]["promocode"],
            user=current_user
        )
        orders.append(current_order)
    Order.objects.bulk_create(orders)
    for i in range(len(orders)):
        orders[i].products.set(raw_orders[i]["products"])
    return orders