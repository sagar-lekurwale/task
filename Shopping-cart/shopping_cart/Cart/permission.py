from rest_framework.permissions import BasePermission,SAFE_METHODS

class IsOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        # Allow GET, HEAD, and OPTIONS requests
        if request.method in SAFE_METHODS:
            return True
        
        # Check if the user is the owner of the object
        return obj.customer.user == request.user
