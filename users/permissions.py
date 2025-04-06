from rest_framework import permissions

class IsRole(permissions.BasePermission):
    role = None
    def has_permission(self, request, view):
        is_authenticated = request.user.is_authenticated
        return is_authenticated 

    def has_object_permission(self, request, view, obj):
        
        if request in permissions.SAFE_METHODS:
            return True 
        else:
            is_role = getattr(request.user, "role",None) == self.role

            return is_role or request.user.role == "admin"
        
class IsPharmacist(IsRole):
    role = "pharmacist"
    
class IsAccountant(IsRole):
    role = "accountant"

class IsCashier(IsRole):
    role = "cashier"
