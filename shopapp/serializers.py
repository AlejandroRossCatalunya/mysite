from rest_framework import serializers

from .models import Product, Order

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = (
            "pk",
            "name",
            "description",
            "price",
            "discount",
            "created_at",
            "archived",
            "preview"
        )

class OrderSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField("user_desc")
    created_at = serializers.SerializerMethodField("formate_datetime")

    def user_desc(self, instance):
        return f"{instance.user.username} ({instance.user.email})"

    def formate_datetime(self, instance):
        return f"{instance.created_at.strftime('%Y-%m-%d %H:%M:%S')}"

    class Meta:
        model = Order
        fields = (
            "pk",
            "delivery_address",
            "promocode",
            "created_at",
            "user",
            "products",
            "receipt"
        )