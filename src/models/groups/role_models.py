"""Role models for group role management."""
from typing import List, Optional
from pydantic import BaseModel

class Permission(BaseModel):
    """Model for a permission."""
    id: str
    action: str
    description: str

class Role(BaseModel):
    """Model for a role."""
    id: str
    name: str
    permissions: List[str]  # List of permission action strings

class GroupRole(BaseModel):
    """Model for a user's role in a group."""
    id: str
    userId: str
    groupId: str
    role: str  # Role name (e.g., "admin", "moderator")

# Request Models
class CreateRoleRequest(BaseModel):
    """Model for creating a role."""
    name: str
    permissions: List[str]  # List of permission action strings

class CreatePermissionRequest(BaseModel):
    """Model for creating a permission."""
    action: str
    description: str

class CreateGroupRoleRequest(BaseModel):
    """Model for assigning a role to a user in a group."""
    userId: str
    groupId: str
    role: str  # Role name

class RemoveGroupRoleRequest(BaseModel):
    """Model for removing a role from a user in a group."""
    userId: str
    groupId: str

# Response Models
class CreateRoleResponse(BaseModel):
    """Model for create role response."""
    success: bool
    message: str
    roleId: Optional[str] = None

class GetRolesResponse(BaseModel):
    """Model for get roles response."""
    success: bool
    message: str
    roles: List[Role] = []

class CreatePermissionResponse(BaseModel):
    """Model for create permission response."""
    success: bool
    message: str
    permissionId: Optional[str] = None

class GetPermissionsResponse(BaseModel):
    """Model for get permissions response."""
    success: bool
    message: str
    permissions: List[Permission] = []

class CreateGroupRoleResponse(BaseModel):
    """Model for create group role response."""
    success: bool
    message: str
    groupRoleId: Optional[str] = None

class GetGroupRolesResponse(BaseModel):
    """Model for get group roles response."""
    success: bool
    message: str
    groupRoles: List[GroupRole] = []

class RemoveGroupRoleResponse(BaseModel):
    """Model for remove group role response."""
    success: bool
    message: str

class GetPermissionResponse(BaseModel):
    """Model for get single permission response."""
    success: bool
    message: str
    permission: Optional[Permission] = None

class GetRoleResponse(BaseModel):
    """Model for get single role response."""
    success: bool
    message: str
    role: Optional[Role] = None

class ModifyPermissionRequest(BaseModel):
    """Model for modifying a permission."""
    permissionId: str
    action: Optional[str] = None
    description: Optional[str] = None

class ModifyPermissionResponse(BaseModel):
    """Model for modify permission response."""
    success: bool
    message: str

class ModifyRoleRequest(BaseModel):
    """Model for modifying a role."""
    roleId: str
    name: Optional[str] = None
    permissions: Optional[List[str]] = None

class ModifyRoleResponse(BaseModel):
    """Model for modify role response."""
    success: bool
    message: str

class ModifyGroupRoleRequest(BaseModel):
    """Model for modifying a group role."""
    userId: str
    groupId: str
    role: str

class ModifyGroupRoleResponse(BaseModel):
    """Model for modify group role response."""
    success: bool
    message: str

class RemovePermissionRequest(BaseModel):
    """Model for removing a permission."""
    permissionId: str

class RemovePermissionResponse(BaseModel):
    """Model for remove permission response."""
    success: bool
    message: str

class RemoveRoleRequest(BaseModel):
    """Model for removing a role."""
    roleId: str

class RemoveRoleResponse(BaseModel):
    """Model for remove role response."""
    success: bool
    message: str

class RemoveRoleFromGroupRequest(BaseModel):
    """Model for removing a role from a group by role name."""
    groupId: str
    role: str

class RemoveRoleFromGroupResponse(BaseModel):
    """Model for remove role from group response."""
    success: bool
    message: str
    removedCount: int = 0

class GroupRoleConfig(BaseModel):
    """Model for a group-specific role configuration."""
    id: str
    groupId: str
    roleName: str
    permissions: List[str]

class CreateGroupRoleConfigRequest(BaseModel):
    """Model for creating a group role configuration."""
    groupId: str
    roleName: str
    permissions: List[str]

class CreateGroupRoleConfigResponse(BaseModel):
    """Model for create group role config response."""
    success: bool
    message: str
    groupRoleId: Optional[str] = None

class GetGroupRoleConfigsRequest(BaseModel):
    """Model for getting group role configurations."""
    groupId: str

class GetGroupRoleConfigsResponse(BaseModel):
    """Model for get group role configs response."""
    success: bool
    message: str
    groupRoles: List[GroupRoleConfig] = []

class UpdateGroupRoleConfigRequest(BaseModel):
    """Model for updating a group role configuration."""
    groupId: str
    roleName: str
    permissions: List[str]

class UpdateGroupRoleConfigResponse(BaseModel):
    """Model for update group role config response."""
    success: bool
    message: str

class DeleteGroupRoleConfigRequest(BaseModel):
    """Model for deleting a group role configuration."""
    groupId: str
    roleName: str

class DeleteGroupRoleConfigResponse(BaseModel):
    """Model for delete group role config response."""
    success: bool
    message: str

