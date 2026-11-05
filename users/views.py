from rest_framework import generics
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle

from .models import User
from .permissions import IsAdminOrRegistration
from .serializers import (
    AdminUserSerializer,
    MeSerializer,
    PasswordChangeSerializer,
    RegistrationSerializer,
)


class UserListCreateView(generics.ListCreateAPIView):
    queryset = User.objects.select_related("profile").order_by("id")
    permission_classes = [IsAdminOrRegistration]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return RegistrationSerializer
        return AdminUserSerializer

    def get_throttles(self):
        if self.request.method == "POST":
            return [ScopedRateThrottle()]
        return []

    throttle_scope = "registration"


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = AdminUserSerializer
    permission_classes = [IsAdminUser]


class MeView(generics.RetrieveUpdateAPIView):
    serializer_class = MeSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class PasswordChangeView(generics.GenericAPIView):
    serializer_class = PasswordChangeSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=204)
