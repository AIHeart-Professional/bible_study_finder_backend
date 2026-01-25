"""Groups routes - HTTP layer (using public_id UUIDs)."""
from fastapi import APIRouter, Query, File, UploadFile, Form
from src.models.groups import (
    CreateGroupRequest,
    CreateGroupResponse,
    InitializeGroupRequest,
    InitializeGroupResponse,
    GetUsersResponse,
    GetGroupChatResponse,
    GetMealsResponse,
    GetStudyPlanResponse,
    GetGroupsResponse,
    GetGroupResponse,
    CreateGroupChatRequest,
    CreateGroupChatResponse,
    CreateWorksheetRequest,
    CreateWorksheetResponse,
    GetWorksheetsResponse,
    JoinGroupRequest,
    JoinGroupResponse,
    LeaveGroupRequest,
    LeaveGroupResponse,
    CreateGroupRequestRequest,
    CreateGroupRequestResponse,
    GetGroupRequestsResponse,
    CreateGroupRoleConfigRequest,
    CreateGroupRoleConfigResponse,
    GetGroupRoleConfigsResponse,
    UpdateGroupRoleConfigRequest,
    UpdateGroupRoleConfigResponse,
    DeleteGroupRoleConfigRequest,
    DeleteGroupRoleConfigResponse,
    UploadWorksheetResponse,
    CreateWorksheetTextRequest,
    CreateWorksheetTextResponse,
)
from src.controller.groups import GroupsController

# Create a router for Groups-related routes
router = APIRouter()

@router.get("/get_groups", response_model=GetGroupsResponse)
async def get_groups():
    """Get all groups."""
    return await GroupsController().get_all_groups()

@router.get("/get_group", response_model=GetGroupResponse)
async def get_group(groupPublicId: str = Query(..., description="Group public_id (UUID)")):
    """Get a single group by public_id (UUID)."""
    return await GroupsController().get_group(groupPublicId=groupPublicId)

@router.get("/get_user_groups", response_model=GetGroupsResponse)
async def get_groups_by_user_id(userPublicId: str = Query(..., description="User public_id (UUID)")):
    """Get all groups that a user is a member of."""
    return await GroupsController().get_groups_by_user_id(userPublicId=userPublicId)

@router.post("/create_group", response_model=CreateGroupResponse)
async def create_group(request: CreateGroupRequest):
    """Create a new group."""
    return await GroupsController().create_group(
        name=request.name,
        description=request.description,
        leaderPublicId=request.leaderUserId,
        location=request.location.dict(),
        image=request.image
    )

@router.post("/initialize_group", response_model=InitializeGroupResponse)
async def initialize_group(request: InitializeGroupRequest):
    """Initialize a group."""
    return await GroupsController().initialize_group(groupPublicId=request.groupPublicId)

@router.get("/get_users", response_model=GetUsersResponse)
async def get_users(groupPublicId: str = Query(..., description="Group public_id (UUID)")):
    """Get all users (members) of a group."""
    return await GroupsController().get_group_users(groupPublicId=groupPublicId)

@router.get("/get_group_chat", response_model=GetGroupChatResponse)
async def get_group_chat(groupPublicId: str = Query(..., description="Group public_id (UUID)")):
    """Get all chat messages for a group."""
    return await GroupsController().get_group_chat(groupPublicId=groupPublicId)

@router.get("/get_meals", response_model=GetMealsResponse)
async def get_meals(groupPublicId: str = Query(..., description="Group public_id (UUID)")):
    """Get all meals for a group."""
    return await GroupsController().get_group_meals(groupPublicId=groupPublicId)

@router.get("/get_study_plan", response_model=GetStudyPlanResponse)
async def get_study_plan(groupPublicId: str = Query(..., description="Group public_id (UUID)")):
    """Get all study plans for a group."""
    return await GroupsController().get_group_study_plans(groupPublicId=groupPublicId)

@router.post("/create_group_chat", response_model=CreateGroupChatResponse)
async def create_group_chat(request: CreateGroupChatRequest):
    """Create a new group chat message."""
    return await GroupsController().create_group_chat(
        groupPublicId=request.groupPublicId,
        userPublicId=request.userPublicId,
        message=request.message
    )

@router.post("/create_worksheet", response_model=CreateWorksheetResponse)
async def create_worksheet(request: CreateWorksheetRequest):
    """Create a new Bible worksheet."""
    return await GroupsController().create_worksheet(
        groupPublicId=request.groupPublicId,
        title=request.title,
        content=request.content
    )

@router.get("/get_worksheets", response_model=GetWorksheetsResponse)
async def get_worksheets(groupPublicId: str = Query(..., description="Group public_id (UUID)")):
    """Get all worksheets for a group."""
    return await GroupsController().get_group_worksheets(groupPublicId=groupPublicId)

@router.post("/upload_worksheet", response_model=UploadWorksheetResponse)
async def upload_worksheet(
    groupPublicId: str = Form(..., description="Group public_id (UUID)"),
    title: str = Form(...),
    file: UploadFile = File(...)
):
    """Upload a worksheet file."""
    return await GroupsController().upload_worksheet(
        groupPublicId=groupPublicId,
        title=title,
        file=file
    )

@router.get("/download_worksheet/{file_id}")
async def download_worksheet(file_id: int):
    """Download a worksheet file."""
    return await GroupsController().download_worksheet_file(file_id)

@router.post("/create_worksheet_text", response_model=CreateWorksheetTextResponse)
async def create_worksheet_text(request: CreateWorksheetTextRequest):
    """Create a worksheet with HTML/text content."""
    return await GroupsController().create_worksheet_text(
        groupPublicId=request.groupPublicId,
        title=request.title,
        content=request.content
    )

@router.post("/join_group", response_model=JoinGroupResponse)
async def join_group(request: JoinGroupRequest):
    """Join a group."""
    return await GroupsController().join_group(
        groupPublicId=request.groupPublicId,
        userPublicId=request.userPublicId
    )

@router.post("/leave_group", response_model=LeaveGroupResponse)
async def leave_group(request: LeaveGroupRequest):
    """Leave a group."""
    return await GroupsController().leave_group(
        groupPublicId=request.groupPublicId,
        userPublicId=request.userPublicId
    )

@router.post("/create_group_request", response_model=CreateGroupRequestResponse)
async def create_group_request(request: CreateGroupRequestRequest):
    """Create a new group request."""
    return await GroupsController().create_group_request(
        groupPublicId=request.groupPublicId,
        userPublicId=request.userPublicId,
        requestMessage=request.requestMessage
    )

@router.get("/get_group_requests", response_model=GetGroupRequestsResponse)
async def get_group_requests(groupPublicId: str = Query(..., description="Group public_id (UUID)")):
    """Get all requests for a group."""
    return await GroupsController().get_group_requests(groupPublicId=groupPublicId)

@router.post("/create_group_role_config", response_model=CreateGroupRoleConfigResponse)
async def create_group_role_config(request: CreateGroupRoleConfigRequest):
    """Create a group role configuration."""
    return await GroupsController().create_group_role_config(
        groupPublicId=request.groupPublicId,
        roleName=request.roleName,
        permissions=request.permissions
    )

@router.get("/get_group_role_configs", response_model=GetGroupRoleConfigsResponse)
async def get_group_role_configs(groupPublicId: str = Query(..., description="Group public_id (UUID)")):
    """Get all role configurations for a group."""
    return await GroupsController().get_group_role_configs(groupPublicId=groupPublicId)

@router.post("/update_group_role_config", response_model=UpdateGroupRoleConfigResponse)
async def update_group_role_config(request: UpdateGroupRoleConfigRequest):
    """Update a group role configuration."""
    return await GroupsController().update_group_role_config(
        groupPublicId=request.groupPublicId,
        roleName=request.roleName,
        permissions=request.permissions
    )

@router.post("/delete_group_role_config", response_model=DeleteGroupRoleConfigResponse)
async def delete_group_role_config(request: DeleteGroupRoleConfigRequest):
    """Delete a group role configuration."""
    return await GroupsController().delete_group_role_config(
        groupPublicId=request.groupPublicId,
        roleName=request.roleName
    )
