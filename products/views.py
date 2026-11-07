from django.shortcuts import get_object_or_404
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from config.pagination import ApiPagination
from config.permissions import IsAdminOrReadOnly

from .models import Product
from .serializers import ProductPageSerializer, ProductSerializer


class ProductListCreateAPIView(APIView):
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = ProductSerializer
    pagination_class = ApiPagination

    @extend_schema(
        operation_id="products_list",
        responses=ProductPageSerializer,
        parameters=[
            OpenApiParameter(
                name="page",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name="page_size",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Number of results per page (maximum: 100).",
            ),
        ],
    )
    def get(self, request):
        products = Product.objects.prefetch_related("categories").order_by("id")
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(products, request, view=self)

        if page is not None:
            serializer = ProductSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        return Response(ProductSerializer(products, many=True).data)

    def post(self, request):
        serializer = ProductSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ProductDetailAPIView(APIView):
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = ProductSerializer

    @extend_schema(operation_id="products_detail")
    def get(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        serializer = ProductSerializer(product)

        return Response(serializer.data)

    def put(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        serializer = ProductSerializer(product, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def patch(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        serializer = ProductSerializer(
            product,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        product.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
