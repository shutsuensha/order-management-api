from django.urls import path

from .views import ProductDetailAPIView, ProductListCreateAPIView

urlpatterns = [
    path("products/", ProductListCreateAPIView.as_view()),
    path("products/<int:pk>/", ProductDetailAPIView.as_view()),
]
