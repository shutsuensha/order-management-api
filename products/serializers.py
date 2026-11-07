from rest_framework import serializers

from .models import Product


class ProductSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(required=True)
    description = serializers.CharField(
        allow_blank=True,
    )

    class Meta:
        model = Product
        fields = ["id", "name", "price", "stock", "description", "categories"]

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than zero.")
        return value

    def validate(self, attrs):
        name = attrs.get("name", self.instance.name if self.instance else None)
        price = attrs.get("price", self.instance.price if self.instance else None)

        if name == "test" and price > 1000:
            raise serializers.ValidationError("Invalid combination")

        return attrs

    def create(self, validated_data):
        categories = validated_data.pop("categories", [])

        product = Product.objects.create(**validated_data)

        product.categories.set(categories)

        return product

    def update(self, instance, validated_data):
        categories = validated_data.pop("categories", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        if categories is not None:
            instance.categories.set(categories)

        return instance


class ProductPageSerializer(serializers.Serializer):
    count = serializers.IntegerField()
    next = serializers.URLField(allow_null=True)
    previous = serializers.URLField(allow_null=True)
    results = ProductSerializer(many=True)
