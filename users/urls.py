from django.urls import path

from .views import UserListCreateView

urlpatterns = [
    path("users/", UserListCreateView.as_view()),
]
