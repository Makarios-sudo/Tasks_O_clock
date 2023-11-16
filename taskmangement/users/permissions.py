from rest_framework import permissions

class IsOrganizationAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_organization_admin
    
class IsOrganizationStaff(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_organization_admin
    
class IsTeamLead(permissions.BasePermission):
    def has_permission(self, request, view, obj):
        return request.user.is_authenticated and request.user.is_organization_admin
   
class IsTeamMember(permissions.BasePermission):
    def has_permission(self, request, view, obj):
        return request.user.is_authenticated and request.user.is_organization_admin
   
class IsOwner(permissions.BasePermission):  
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user