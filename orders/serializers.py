from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction
from rest_framework import serializers

from products.models import Product
from users.serializers import UserSerializer

from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        source="product",
        queryset=Product.objects.all(),
        write_only=True,
    )
    line_total = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "product",
            "product_id",
            "quantity",
            "product_name",
            "unit_price",
            "line_total",
        ]
        read_only_fields = ["product_name", "unit_price"]

    def get_line_total(self, item: OrderItem) -> str:
        return f"{item.unit_price * item.quantity:.2f}"


class OrderSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(source="user", read_only=True)
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "user",
            "user_id",
            "number",
            "total",
            "status",
            "items",
        ]
        read_only_fields = ["number", "total"]

    def validate(self, attrs):
        if "total" in self.initial_data:
            raise serializers.ValidationError(
                {"total": "Total is calculated from order items."}
            )

        request = self.context.get("request")
        requested_status = attrs.get("status")
        protected_statuses = {
            Order.Status.PAID,
            Order.Status.COMPLETED,
        }
        if (
            request
            and requested_status in protected_statuses
            and not request.user.is_staff
        ):
            raise serializers.ValidationError(
                {"status": "Only an administrator can set this status."}
            )

        return attrs

    @staticmethod
    def _create_items(order: Order, items_data: list[dict]) -> Decimal:
        total = Decimal("0.00")
        for item_data in items_data:
            product = item_data["product"]
            quantity = item_data["quantity"]
            item_price = product.price

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                product_name=product.name,
                unit_price=item_price,
            )
            total += item_price * quantity

        return total

    @transaction.atomic
    def create(self, validated_data):
        items_data = validated_data.pop("items")
        order = Order.objects.create(total=Decimal("0.00"), **validated_data)
        order.total = self._create_items(order, items_data)
        order.save(update_fields=["total"])
        return order

    @transaction.atomic
    def update(self, instance, validated_data):
        items_data = validated_data.pop("items", None)
        status = validated_data.pop("status", None)

        if status is not None:
            try:
                instance.transition_to(status)
            except ValidationError as exc:
                raise serializers.ValidationError({"status": exc.messages}) from exc

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if items_data is not None:
            instance.items.all().delete()
            instance.total = self._create_items(instance, items_data)

        instance.save()
        return instance
