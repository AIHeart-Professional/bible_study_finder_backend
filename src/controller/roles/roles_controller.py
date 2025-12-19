"""Roles controller - Business logic distributor layer."""
from typing import Optional
from src.models.groups.role_models import (
    CreateRoleResponse,
    GetRolesResponse,
    GetRoleResponse,
    CreatePermissionResponse,
    GetPermissionsResponse,
    GetPermissionResponse,
    CreateGroupRoleResponse,
    GetGroupRolesResponse,
    RemoveGroupRoleResponse,
    ModifyPermissionRequest,
    ModifyPermissionResponse,
    ModifyRoleRequest,
    ModifyRoleResponse,
    ModifyGroupRoleRequest,
    ModifyGroupRoleResponse,
    RemovePermissionRequest,
    RemovePermissionResponse,
    RemoveRoleRequest,
    RemoveRoleResponse,
    RemoveRoleFromGroupRequest,
    RemoveRoleFromGroupResponse
)
from src.utils.logger import get_logger
from src.services.roles_service import RolesService

class RolesController:
    """Controller for handling role business logic."""
    
    def __init__(self):
        """Initialize the controller and roles service."""
        self.roles_service = RolesService()
        self.logger = get_logger(__name__)
    
    async def create_permission(
        self,
        action: str,
        description: str
    ) -> CreatePermissionResponse:
        """Create a new permission."""
        try:
            success, message, permission_id = await self.roles_service.create_permission(
                action=action,
                description=description
            )
            
            return CreatePermissionResponse(
                success=success,
                message=message,
                permissionId=permission_id
            )
        except Exception as e:
            self.logger.error(f"Error in create_permission controller: {e}")
            return CreatePermissionResponse(
                success=False,
                message=f"Error creating permission: {str(e)}",
                permissionId=None
            )
    
    async def get_all_permissions(self) -> GetPermissionsResponse:
        """Get all permissions."""
        try:
            success, message, permissions = await self.roles_service.get_all_permissions()
            
            return GetPermissionsResponse(
                success=success,
                message=message,
                permissions=permissions
            )
        except Exception as e:
            self.logger.error(f"Error in get_all_permissions controller: {e}")
            return GetPermissionsResponse(
                success=False,
                message=f"Error getting permissions: {str(e)}",
                permissions=[]
            )
    
    async def create_role(
        self,
        name: str,
        permissions: list[str]
    ) -> CreateRoleResponse:
        """Create a new role."""
        try:
            success, message, role_id = await self.roles_service.create_role(
                name=name,
                permissions=permissions
            )
            
            return CreateRoleResponse(
                success=success,
                message=message,
                roleId=role_id
            )
        except Exception as e:
            self.logger.error(f"Error in create_role controller: {e}")
            return CreateRoleResponse(
                success=False,
                message=f"Error creating role: {str(e)}",
                roleId=None
            )
    
    async def get_all_roles(self) -> GetRolesResponse:
        """Get all roles."""
        try:
            success, message, roles = await self.roles_service.get_all_roles()
            
            return GetRolesResponse(
                success=success,
                message=message,
                roles=roles
            )
        except Exception as e:
            self.logger.error(f"Error in get_all_roles controller: {e}")
            return GetRolesResponse(
                success=False,
                message=f"Error getting roles: {str(e)}",
                roles=[]
            )
    
    async def create_group_role(
        self,
        userId: str,
        groupId: str,
        role: str
    ) -> CreateGroupRoleResponse:
        """Assign a role to a user in a group."""
        try:
            success, message, group_role_id = await self.roles_service.create_group_role(
                userId=userId,
                groupId=groupId,
                role=role
            )
            
            return CreateGroupRoleResponse(
                success=success,
                message=message,
                groupRoleId=group_role_id
            )
        except Exception as e:
            self.logger.error(f"Error in create_group_role controller: {e}")
            return CreateGroupRoleResponse(
                success=False,
                message=f"Error creating group role: {str(e)}",
                groupRoleId=None
            )
    
    async def get_group_roles(
        self,
        groupId: Optional[str] = None,
        userId: Optional[str] = None
    ) -> GetGroupRolesResponse:
        """Get group roles, optionally filtered by groupId or userId."""
        try:
            success, message, group_roles = await self.roles_service.get_group_roles(
                groupId=groupId,
                userId=userId
            )
            
            return GetGroupRolesResponse(
                success=success,
                message=message,
                groupRoles=group_roles
            )
        except Exception as e:
            self.logger.error(f"Error in get_group_roles controller: {e}")
            return GetGroupRolesResponse(
                success=False,
                message=f"Error getting group roles: {str(e)}",
                groupRoles=[]
            )
    
    async def remove_group_role(
        self,
        userId: str,
        groupId: str
    ) -> RemoveGroupRoleResponse:
        """Remove a role from a user in a group."""
        try:
            success, message = await self.roles_service.remove_group_role(
                userId=userId,
                groupId=groupId
            )
            
            return RemoveGroupRoleResponse(
                success=success,
                message=message
            )
        except Exception as e:
            self.logger.error(f"Error in remove_group_role controller: {e}")
            return RemoveGroupRoleResponse(
                success=False,
                message=f"Error removing group role: {str(e)}"
            )
    
    async def get_permission(self, permissionId: str) -> GetPermissionResponse:
        """Get a single permission by ID."""
        try:
            success, message, permission = await self.roles_service.get_permission(permissionId)
            
            return GetPermissionResponse(
                success=success,
                message=message,
                permission=permission
            )
        except Exception as e:
            self.logger.error(f"Error in get_permission controller: {e}")
            return GetPermissionResponse(
                success=False,
                message=f"Error getting permission: {str(e)}",
                permission=None
            )
    
    async def modify_permission(self, request: ModifyPermissionRequest) -> ModifyPermissionResponse:
        """Modify a permission."""
        try:
            success, message = await self.roles_service.modify_permission(
                permissionId=request.permissionId,
                action=request.action,
                description=request.description
            )
            
            return ModifyPermissionResponse(
                success=success,
                message=message
            )
        except Exception as e:
            self.logger.error(f"Error in modify_permission controller: {e}")
            return ModifyPermissionResponse(
                success=False,
                message=f"Error modifying permission: {str(e)}"
            )
    
    async def get_role(self, roleId: str) -> GetRoleResponse:
        """Get a single role by ID."""
        try:
            success, message, role = await self.roles_service.get_role(roleId)
            
            return GetRoleResponse(
                success=success,
                message=message,
                role=role
            )
        except Exception as e:
            self.logger.error(f"Error in get_role controller: {e}")
            return GetRoleResponse(
                success=False,
                message=f"Error getting role: {str(e)}",
                role=None
            )
    
    async def modify_role(self, request: ModifyRoleRequest) -> ModifyRoleResponse:
        """Modify a role."""
        try:
            success, message = await self.roles_service.modify_role(
                roleId=request.roleId,
                name=request.name,
                permissions=request.permissions
            )
            
            return ModifyRoleResponse(
                success=success,
                message=message
            )
        except Exception as e:
            self.logger.error(f"Error in modify_role controller: {e}")
            return ModifyRoleResponse(
                success=False,
                message=f"Error modifying role: {str(e)}"
            )
    
    async def modify_group_role(self, request: ModifyGroupRoleRequest) -> ModifyGroupRoleResponse:
        """Modify a group role."""
        try:
            success, message = await self.roles_service.modify_group_role(
                userId=request.userId,
                groupId=request.groupId,
                role=request.role
            )
            
            return ModifyGroupRoleResponse(
                success=success,
                message=message
            )
        except Exception as e:
            self.logger.error(f"Error in modify_group_role controller: {e}")
            return ModifyGroupRoleResponse(
                success=False,
                message=f"Error modifying group role: {str(e)}"
            )
    
    async def remove_permission(self, request: RemovePermissionRequest) -> RemovePermissionResponse:
        """Remove a permission."""
        try:
            success, message = await self.roles_service.remove_permission(request.permissionId)
            
            return RemovePermissionResponse(
                success=success,
                message=message
            )
        except Exception as e:
            self.logger.error(f"Error in remove_permission controller: {e}")
            return RemovePermissionResponse(
                success=False,
                message=f"Error removing permission: {str(e)}"
            )
    
    async def remove_role(self, request: RemoveRoleRequest) -> RemoveRoleResponse:
        """Remove a role."""
        try:
            success, message = await self.roles_service.remove_role(request.roleId)
            
            return RemoveRoleResponse(
                success=success,
                message=message
            )
        except Exception as e:
            self.logger.error(f"Error in remove_role controller: {e}")
            return RemoveRoleResponse(
                success=False,
                message=f"Error removing role: {str(e)}"
            )
    
    async def remove_role_from_group(self, request: RemoveRoleFromGroupRequest) -> RemoveRoleFromGroupResponse:
        """Remove all group roles matching a specific role name from a group."""
        try:
            success, message, removed_count = await self.roles_service.remove_role_from_group(
                groupId=request.groupId,
                role=request.role
            )
            
            return RemoveRoleFromGroupResponse(
                success=success,
                message=message,
                removedCount=removed_count
            )
        except Exception as e:
            self.logger.error(f"Error in remove_role_from_group controller: {e}")
            return RemoveRoleFromGroupResponse(
                success=False,
                message=f"Error removing role from group: {str(e)}",
                removedCount=0
            )

