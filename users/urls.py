from django.urls import path

from .views import UserDetailView, UserListCreateView

urlpatterns = [
    path("users/", UserListCreateView.as_view()),
    path("users/<int:pk>/", UserDetailView.as_view()),
]
