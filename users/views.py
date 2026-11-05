from rest_framework import generics
from rest_framework.permissions import IsAdminUser

from .models import User
from .permissions import IsAdminOrRegistration
from .serializers import UserSerializer


class UserListCreateView(generics.ListCreateAPIView):
    queryset = User.objects.select_related("profile")
    serializer_class = UserSerializer
    permission_classes = [IsAdminOrRegistration]


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]
