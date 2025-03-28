from rest_framework.permissions import BasePermission

class IsRole(BasePermission):
    role = None
    def has_permission(self, request, view):
        is_authenticated = request.user.is_authenticated
        is_role = getattr(request.user, "role",None) == self.role
        return is_authenticated and is_role
        
        
class IsPharmacist(IsRole):
    role = "pharmacist"
    
class IsAccountant(IsRole):
    role = "accountant"

class IsCashier(IsRole):
    role = "cashier"
