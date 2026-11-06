from django.urls import path

from .views import OrderCancelView, OrderDetailView, OrderListCreateView

urlpatterns = [
    path("orders/", OrderListCreateView.as_view()),
    path("orders/<int:pk>/cancel/", OrderCancelView.as_view()),
    path("orders/<int:pk>/", OrderDetailView.as_view()),
]
