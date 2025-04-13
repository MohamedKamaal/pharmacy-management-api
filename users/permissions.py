from rest_framework import permissions

class IsRole(permissions.BasePermission):
    role = None
    def has_permission(self, request, view):
        is_authenticated = request.user.is_authenticated
        if is_authenticated:
            if request.method in permissions.SAFE_METHODS:
                return True 
            else:
                
                is_role = getattr(request.user, "role",None) == self.role

                return is_role or request.user.role == "admin"
                   
                
        return False 
    
    def has_object_permission(self, request, view, obj):
        
        is_authenticated = request.user.is_authenticated
        if is_authenticated:
            if request.method in permissions.SAFE_METHODS:
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


class IsPharmacistOnly(permissions.BasePermission):
    role = "pharmacist"

    def has_permission(self, request, view):
        # Ensure the user is authenticated
        if not request.user.is_authenticated:
            return False
        
       
        
        # Check if the user's role matches the required role, or they are an admin
        return getattr(request.user, "role", None) == self.role or request.user.role == "admin"
    
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        
       
        
        return getattr(request.user, "role", None) == self.role or request.user.role == "admin"