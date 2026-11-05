from rest_framework.permissions import SAFE_METHODS, BasePermission, IsAdminUser


class IsAdminOrReadOnly(BasePermission):
    """Allow public reads and restrict catalog mutations to administrators."""

    def has_permission(self, request, view) -> bool:
        if request.method in SAFE_METHODS:
            return True
        return IsAdminUser().has_permission(request, view)
