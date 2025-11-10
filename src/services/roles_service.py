"""Roles service - Application logic layer."""
from typing import List, Optional
from src.models.groups.role_models import (
    Role,
    Permission,
    GroupRole
)
from src.utils.logger import get_logger
from src.database.groups.groups_database import GroupsDatabase

class RolesService:
    """Service for handling role business logic."""
    
    def __init__(self):
        """Initialize the service and database."""
        self.logger = get_logger(__name__)
        self.groups_database = GroupsDatabase()
        self.logger.info("RolesService initialized successfully")
    
    async def create_permission(self, action: str, description: str) -> tuple[bool, str, Optional[str]]:
        """Create a new permission."""
        try:
            permission_id = await self.groups_database.create_permission(action, description)
            if permission_id:
                return True, "Permission created successfully", permission_id
            else:
                return False, "Failed to create permission (may already exist)", None
        except Exception as e:
            self.logger.error(f"Error creating permission: {e}")
            return False, f"Error creating permission: {str(e)}", None
    
    async def get_all_permissions(self) -> tuple[bool, str, List[Permission]]:
        """Get all permissions."""
        try:
            permissions_data = await self.groups_database.get_all_permissions()
            permissions = [
                Permission(
                    id=perm['id'],
                    action=perm['action'],
                    description=perm['description']
                )
                for perm in permissions_data
            ]
            return True, "Permissions retrieved successfully", permissions
        except Exception as e:
            self.logger.error(f"Error getting permissions: {e}")
            return False, f"Error getting permissions: {str(e)}", []
    
    async def get_permission(self, permissionId: str) -> tuple[bool, str, Optional[Permission]]:
        """Get a single permission by ID."""
        try:
            permission_data = await self.groups_database.get_permission_by_id(permissionId)
            if not permission_data:
                return False, "Permission not found", None
            
            permission = Permission(
                id=permission_data['id'],
                action=permission_data['action'],
                description=permission_data['description']
            )
            return True, "Permission retrieved successfully", permission
        except Exception as e:
            self.logger.error(f"Error getting permission: {e}")
            return False, f"Error getting permission: {str(e)}", None
    
    async def modify_permission(
        self,
        permissionId: str,
        action: Optional[str] = None,
        description: Optional[str] = None
    ) -> tuple[bool, str]:
        """Modify a permission."""
        try:
            success = await self.groups_database.update_permission(
                permissionId=permissionId,
                action=action,
                description=description
            )
            
            if success:
                return True, "Permission updated successfully"
            else:
                return False, "Permission not found or no changes made"
        except Exception as e:
            self.logger.error(f"Error modifying permission: {e}")
            return False, f"Error modifying permission: {str(e)}"
    
    async def create_role(self, name: str, permissions: List[str]) -> tuple[bool, str, Optional[str]]:
        """Create a new role."""
        try:
            # Validate that all permissions exist
            all_permissions_data = await self.groups_database.get_all_permissions()
            valid_actions = {perm['action'] for perm in all_permissions_data}
            
            invalid_permissions = [p for p in permissions if p not in valid_actions]
            if invalid_permissions:
                return False, f"Invalid permissions: {invalid_permissions}", None
            
            role_id = await self.groups_database.create_role(name, permissions)
            if role_id:
                return True, "Role created successfully", role_id
            else:
                return False, "Failed to create role (may already exist)", None
        except Exception as e:
            self.logger.error(f"Error creating role: {e}")
            return False, f"Error creating role: {str(e)}", None
    
    async def get_all_roles(self) -> tuple[bool, str, List[Role]]:
        """Get all roles."""
        try:
            roles_data = await self.groups_database.get_all_roles()
            roles = [
                Role(
                    id=role['id'],
                    name=role['name'],
                    permissions=role['permissions']
                )
                for role in roles_data
            ]
            return True, "Roles retrieved successfully", roles
        except Exception as e:
            self.logger.error(f"Error getting roles: {e}")
            return False, f"Error getting roles: {str(e)}", []
    
    async def get_role(self, roleId: str) -> tuple[bool, str, Optional[Role]]:
        """Get a single role by ID."""
        try:
            role_data = await self.groups_database.get_role_by_id(roleId)
            if not role_data:
                return False, "Role not found", None
            
            role = Role(
                id=role_data['id'],
                name=role_data['name'],
                permissions=role_data['permissions']
            )
            return True, "Role retrieved successfully", role
        except Exception as e:
            self.logger.error(f"Error getting role: {e}")
            return False, f"Error getting role: {str(e)}", None
    
    async def modify_role(
        self,
        roleId: str,
        name: Optional[str] = None,
        permissions: Optional[List[str]] = None
    ) -> tuple[bool, str]:
        """Modify a role."""
        try:
            # If permissions are being updated, validate they exist
            if permissions is not None:
                all_permissions_data = await self.groups_database.get_all_permissions()
                valid_actions = {perm['action'] for perm in all_permissions_data}
                
                invalid_permissions = [p for p in permissions if p not in valid_actions]
                if invalid_permissions:
                    return False, f"Invalid permissions: {invalid_permissions}"
            
            success = await self.groups_database.update_role(
                roleId=roleId,
                name=name,
                permissions=permissions
            )
            
            if success:
                return True, "Role updated successfully"
            else:
                return False, "Role not found or no changes made"
        except Exception as e:
            self.logger.error(f"Error modifying role: {e}")
            return False, f"Error modifying role: {str(e)}"
    
    async def create_group_role(
        self,
        userId: str,
        groupId: str,
        role: str
    ) -> tuple[bool, str, Optional[str]]:
        """Assign a role to a user in a group."""
        try:
            # Validate role exists
            role_doc = await self.groups_database.get_role_by_name(role)
            if not role_doc:
                return False, f"Role '{role}' does not exist", None
            
            # Check if group exists
            group = await self.groups_database.get_group_by_id(groupId)
            if not group:
                return False, "Group not found", None
            
            group_role_id = await self.groups_database.create_group_role(userId, groupId, role)
            if group_role_id:
                return True, "Group role assigned successfully", group_role_id
            else:
                return False, "Failed to assign group role", None
        except Exception as e:
            self.logger.error(f"Error creating group role: {e}")
            return False, f"Error creating group role: {str(e)}", None
    
    async def get_group_roles(
        self,
        groupId: Optional[str] = None,
        userId: Optional[str] = None
    ) -> tuple[bool, str, List[GroupRole]]:
        """Get group roles, optionally filtered by groupId or userId."""
        try:
            group_roles_data = await self.groups_database.get_group_roles(groupId, userId)
            group_roles = [
                GroupRole(
                    id=gr['id'],
                    userId=gr['userId'],
                    groupId=gr['groupId'],
                    role=gr['role']
                )
                for gr in group_roles_data
            ]
            return True, "Group roles retrieved successfully", group_roles
        except Exception as e:
            self.logger.error(f"Error getting group roles: {e}")
            return False, f"Error getting group roles: {str(e)}", []
    
    async def remove_group_role(self, userId: str, groupId: str) -> tuple[bool, str]:
        """Remove a role from a user in a group."""
        try:
            success = await self.groups_database.remove_group_role(userId, groupId)
            if success:
                return True, "Group role removed successfully"
            else:
                return False, "Group role not found"
        except Exception as e:
            self.logger.error(f"Error removing group role: {e}")
            return False, f"Error removing group role: {str(e)}"
    
    async def modify_group_role(
        self,
        userId: str,
        groupId: str,
        role: str
    ) -> tuple[bool, str]:
        """Modify a group role."""
        try:
            # Validate role exists
            role_doc = await self.groups_database.get_role_by_name(role)
            if not role_doc:
                return False, f"Role '{role}' does not exist"
            
            # Check if group exists
            group = await self.groups_database.get_group_by_id(groupId)
            if not group:
                return False, "Group not found"
            
            success = await self.groups_database.update_group_role(userId, groupId, role)
            if success:
                return True, "Group role updated successfully"
            else:
                return False, "Group role not found"
        except Exception as e:
            self.logger.error(f"Error modifying group role: {e}")
            return False, f"Error modifying group role: {str(e)}"
    
    async def remove_permission(self, permissionId: str) -> tuple[bool, str]:
        """Remove a permission."""
        try:
            success = await self.groups_database.remove_permission(permissionId)
            if success:
                return True, "Permission removed successfully"
            else:
                return False, "Permission not found"
        except Exception as e:
            self.logger.error(f"Error removing permission: {e}")
            return False, f"Error removing permission: {str(e)}"
    
    async def remove_role(self, roleId: str) -> tuple[bool, str]:
        """Remove a role."""
        try:
            success = await self.groups_database.remove_role(roleId)
            if success:
                return True, "Role removed successfully"
            else:
                return False, "Role not found"
        except Exception as e:
            self.logger.error(f"Error removing role: {e}")
            return False, f"Error removing role: {str(e)}"
    
    async def remove_role_from_group(self, groupId: str, role: str) -> tuple[bool, str, int]:
        """Remove all group roles matching a specific role name from a group."""
        try:
            # Check if group exists
            group = await self.groups_database.get_group_by_id(groupId)
            if not group:
                return False, "Group not found", 0
            
            removed_count = await self.groups_database.remove_role_from_group(groupId, role)
            
            if removed_count > 0:
                return True, f"Removed {removed_count} group role(s) with role '{role}' from group", removed_count
            else:
                return False, f"No group roles found with role '{role}' in group", 0
        except Exception as e:
            self.logger.error(f"Error removing role from group: {e}")
            return False, f"Error removing role from group: {str(e)}", 0

