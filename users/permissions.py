from rest_framework import permissions

class IsRole(permissions.BasePermission):
    """
    Base permission class to restrict access based on the user's role.
    """
    role = None

    def has_permission(self, request, view):
        is_authenticated = request.user.is_authenticated
        if is_authenticated:
            if request.method in permissions.SAFE_METHODS:
                return True
            is_role = getattr(request.user, "role", None) == self.role
            return is_role or request.user.role == "admin"
        return False

    def has_object_permission(self, request, view, obj):
        is_authenticated = request.user.is_authenticated
        if is_authenticated:
            if request.method in permissions.SAFE_METHODS:
                return True
            is_role = getattr(request.user, "role", None) == self.role
            return is_role or request.user.role == "admin"
        return False


class IsPharmacist(IsRole):
    """
    Permission class allowing only Pharmacists or Admins.
    """
    role = "pharmacist"


class IsAccountant(IsRole):
    """
    Permission class allowing only Accountants or Admins.
    """
    role = "accountant"


class IsCashier(IsRole):
    """
    Permission class allowing only Cashiers or Admins.
    """
    role = "cashier"


class IsPharmacistOnly(permissions.BasePermission):
    """
    Dedicated permission class strictly for Pharmacists and Admins.
    """

    role = "pharmacist"

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return getattr(request.user, "role", None) == self.role or request.user.role == "admin"

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        return getattr(request.user, "role", None) == self.role or request.user.role == "admin"
