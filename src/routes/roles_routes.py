"""Roles routes - HTTP layer."""
from fastapi import APIRouter, Query
from src.models.groups.role_models import (
    CreateRoleRequest,
    CreateRoleResponse,
    GetRolesResponse,
    GetRoleResponse,
    CreatePermissionRequest,
    CreatePermissionResponse,
    GetPermissionsResponse,
    GetPermissionResponse,
    CreateGroupRoleRequest,
    CreateGroupRoleResponse,
    GetGroupRolesResponse,
    RemoveGroupRoleRequest,
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
from src.controller.roles.roles_controller import RolesController

# Create a router for Roles-related routes
router = APIRouter()


@router.post("/create_permission", response_model=CreatePermissionResponse)
async def create_permission(request: CreatePermissionRequest):
    """
    Create a new permission.
    
    Request Body:
        action: Permission action name (e.g., "edit_group_info")
        description: Description of what this permission allows
    
    Returns:
        CreatePermissionResponse with creation status and permission ID
    """
    controller = RolesController()
    return await controller.create_permission(
        action=request.action,
        description=request.description
    )


@router.get("/get_permissions", response_model=GetPermissionsResponse)
async def get_permissions():
    """
    Get all permissions.
    
    Returns:
        GetPermissionsResponse with list of all permissions
    """
    controller = RolesController()
    return await controller.get_all_permissions()


@router.post("/create_role", response_model=CreateRoleResponse)
async def create_role(request: CreateRoleRequest):
    """
    Create a new role.
    
    Request Body:
        name: Role name (e.g., "admin", "moderator")
        permissions: List of permission action strings
    
    Returns:
        CreateRoleResponse with creation status and role ID
    """
    controller = RolesController()
    return await controller.create_role(
        name=request.name,
        permissions=request.permissions
    )


@router.get("/get_roles", response_model=GetRolesResponse)
async def get_roles():
    """
    Get all roles.
    
    Returns:
        GetRolesResponse with list of all roles
    """
    controller = RolesController()
    return await controller.get_all_roles()


@router.post("/create_group_role", response_model=CreateGroupRoleResponse)
async def create_group_role(request: CreateGroupRoleRequest):
    """
    Assign a role to a user in a group.
    
    Request Body:
        userId: ID of the user
        groupId: ID of the group
        role: Role name to assign
    
    Returns:
        CreateGroupRoleResponse with creation status and group role ID
    """
    controller = RolesController()
    return await controller.create_group_role(
        userId=request.userId,
        groupId=request.groupId,
        role=request.role
    )


@router.get("/get_group_roles", response_model=GetGroupRolesResponse)
async def get_group_roles(
    groupId: str = Query(None, description="Filter by group ID"),
    userId: str = Query(None, description="Filter by user ID")
):
    """
    Get group roles, optionally filtered by groupId or userId.
    
    Query Parameters:
        groupId: Optional - Filter by group ID
        userId: Optional - Filter by user ID
    
    Returns:
        GetGroupRolesResponse with list of group roles
    """
    controller = RolesController()
    return await controller.get_group_roles(
        groupId=groupId,
        userId=userId
    )


@router.post("/remove_group_role", response_model=RemoveGroupRoleResponse)
async def remove_group_role(request: RemoveGroupRoleRequest):
    """
    Remove a role from a user in a group.
    
    Request Body:
        userId: ID of the user
        groupId: ID of the group
    
    Returns:
        RemoveGroupRoleResponse with removal status
    """
    controller = RolesController()
    return await controller.remove_group_role(
        userId=request.userId,
        groupId=request.groupId
    )


@router.get("/get_permission", response_model=GetPermissionResponse)
async def get_permission(permissionId: str = Query(..., description="Permission ID")):
    """
    Get a single permission by ID.
    
    Query Parameters:
        permissionId: ID of the permission
    
    Returns:
        GetPermissionResponse with permission data
    """
    controller = RolesController()
    return await controller.get_permission(permissionId=permissionId)


@router.post("/modify_permission", response_model=ModifyPermissionResponse)
async def modify_permission(request: ModifyPermissionRequest):
    """
    Modify a permission.
    
    Request Body:
        permissionId: ID of the permission to modify
        action: Optional - New action name
        description: Optional - New description
    
    Returns:
        ModifyPermissionResponse with update status
    """
    controller = RolesController()
    return await controller.modify_permission(request=request)


@router.get("/get_role", response_model=GetRoleResponse)
async def get_role(roleId: str = Query(..., description="Role ID")):
    """
    Get a single role by ID.
    
    Query Parameters:
        roleId: ID of the role
    
    Returns:
        GetRoleResponse with role data
    """
    controller = RolesController()
    return await controller.get_role(roleId=roleId)


@router.post("/modify_role", response_model=ModifyRoleResponse)
async def modify_role(request: ModifyRoleRequest):
    """
    Modify a role.
    
    Request Body:
        roleId: ID of the role to modify
        name: Optional - New role name
        permissions: Optional - New list of permission actions
    
    Returns:
        ModifyRoleResponse with update status
    """
    controller = RolesController()
    return await controller.modify_role(request=request)


@router.post("/modify_group_role", response_model=ModifyGroupRoleResponse)
async def modify_group_role(request: ModifyGroupRoleRequest):
    """
    Modify a group role.
    
    Request Body:
        userId: ID of the user
        groupId: ID of the group
        role: New role name to assign
    
    Returns:
        ModifyGroupRoleResponse with update status
    """
    controller = RolesController()
    return await controller.modify_group_role(request=request)


@router.post("/remove_permission", response_model=RemovePermissionResponse)
async def remove_permission(request: RemovePermissionRequest):
    """
    Remove a permission.
    
    Request Body:
        permissionId: ID of the permission to remove
    
    Returns:
        RemovePermissionResponse with removal status
    """
    controller = RolesController()
    return await controller.remove_permission(request=request)


@router.post("/remove_role", response_model=RemoveRoleResponse)
async def remove_role(request: RemoveRoleRequest):
    """
    Remove a role.
    
    Request Body:
        roleId: ID of the role to remove
    
    Returns:
        RemoveRoleResponse with removal status
    """
    controller = RolesController()
    return await controller.remove_role(request=request)


@router.post("/remove_role_from_group", response_model=RemoveRoleFromGroupResponse)
async def remove_role_from_group(request: RemoveRoleFromGroupRequest):
    """
    Remove all group roles matching a specific role name from a group.
    
    Request Body:
        groupId: ID of the group
        role: Role name to remove (e.g., "admin", "moderator")
    
    Returns:
        RemoveRoleFromGroupResponse with removal status and count of removed roles
    """
    controller = RolesController()
    return await controller.remove_role_from_group(request=request)

