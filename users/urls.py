from django.urls import path

from .views import MeView, PasswordChangeView, UserDetailView, UserListCreateView

urlpatterns = [
    path("auth/me/", MeView.as_view()),
    path("auth/change-password/", PasswordChangeView.as_view()),
    path("users/", UserListCreateView.as_view()),
    path("users/<int:pk>/", UserDetailView.as_view()),
]
