from rest_framework.permissions import BasePermission, IsAdminUser


class IsAdminOrRegistration(BasePermission):
    """Allow anonymous registration, but restrict user management to admins."""

    def has_permission(self, request, view) -> bool:
        return request.method == "POST" or IsAdminUser().has_permission(request, view)
