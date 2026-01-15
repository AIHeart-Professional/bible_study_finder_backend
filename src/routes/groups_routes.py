"""Groups routes - HTTP layer."""
from fastapi import APIRouter, Query, File, UploadFile, Form
from fastapi.responses import StreamingResponse
from src.models.groups import (
    CreateGroupRequest,
    CreateGroupResponse,
    InitializeGroupRequest,
    InitializeGroupResponse,
    GetUsersResponse,
    GetChatResponse,
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
    GetGroupRoleConfigsRequest,
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
    """
    Get all groups.
    
    Returns:
        GetGroupsResponse with list of all groups
    """
    controller = GroupsController()
    return await controller.get_all_groups()


@router.get("/get_group", response_model=GetGroupResponse)
async def get_group(groupId: str):
    """
    Get a single group by ID.
    
    Query Parameters:
        groupId: ID of the group to retrieve
    
    Returns:
        GetGroupResponse with group information
    """
    controller = GroupsController()
    return await controller.get_group(groupId=groupId)


@router.get("/get_user_groups", response_model=GetGroupsResponse)
async def get_groups_by_user_id(userId: str = Query(...)):
    """
    Get all groups that a user is a member of.
    
    Query Parameters:
        userId: ID of the user
    
    Returns:
        GetGroupsResponse with list of groups the user is a member of
    """
    controller = GroupsController()
    return await controller.get_groups_by_user_id(userId=userId)


@router.post("/create_group", response_model=CreateGroupResponse)
async def create_group(request: CreateGroupRequest):
    """
    Create a new group.
    
    Request Body:
        name: Group name
        description: Group description
        leaderUserId: ID of the group leader
        location: Location information
        image: Optional image URL
    
    Returns:
        CreateGroupResponse with creation status and group ID
    """
    controller = GroupsController()
    return await controller.create_group(
        name=request.name,
        description=request.description,
        leaderUserId=request.leaderUserId,
        location=request.location.dict(),
        image=request.image
    )


@router.post("/initialize_group", response_model=InitializeGroupResponse)
async def initialize_group(request: InitializeGroupRequest):
    """
    Initialize a group with empty arrays for studyPlans and meals.
    
    Request Body:
        groupId: ID of the group to initialize
    
    Returns:
        InitializeGroupResponse with initialization status
    """
    controller = GroupsController()
    return await controller.initialize_group(groupId=request.groupId)


@router.get("/get_users", response_model=GetUsersResponse)
async def get_users(groupId: str = Query(..., description="ID of the group")):
    """
    Get all users (members) of a group.
    
    Query Parameters:
        groupId: ID of the group
    
    Returns:
        GetUsersResponse with list of group members
    """
    controller = GroupsController()
    return await controller.get_group_users(groupId=groupId)


@router.get("/get_chat", response_model=GetChatResponse)
async def get_chat(groupId: str = Query(..., description="ID of the group")):
    """
    Get all chat messages for a group.
    
    Query Parameters:
        groupId: ID of the group
    
    Returns:
        GetChatResponse with list of chat messages
    """
    controller = GroupsController()
    return await controller.get_group_chat(groupId=groupId)


@router.get("/get_meals", response_model=GetMealsResponse)
async def get_meals(groupId: str = Query(..., description="ID of the group")):
    """
    Get all meals for a group.
    
    Query Parameters:
        groupId: ID of the group
    
    Returns:
        GetMealsResponse with list of meals
    """
    controller = GroupsController()
    return await controller.get_group_meals(groupId=groupId)


@router.get("/get_study_plan", response_model=GetStudyPlanResponse)
async def get_study_plan(groupId: str = Query(..., description="ID of the group")):
    """
    Get all study plans for a group.
    
    Query Parameters:
        groupId: ID of the group
    
    Returns:
        GetStudyPlanResponse with list of study plans
    """
    controller = GroupsController()
    return await controller.get_group_study_plans(groupId=groupId)


@router.post("/create_group_chat", response_model=CreateGroupChatResponse)
async def create_group_chat(request: CreateGroupChatRequest):
    """
    Create a new group chat message.
    
    Request Body:
        groupId: ID of the group
        userId: ID of the user sending the message
        message: The chat message content
    
    Returns:
        CreateGroupChatResponse with creation status and chat ID
    """
    controller = GroupsController()
    return await controller.create_group_chat(
        groupId=request.groupId,
        userId=request.userId,
        message=request.message
    )


@router.post("/create_worksheet", response_model=CreateWorksheetResponse)
async def create_worksheet(request: CreateWorksheetRequest):
    """
    Create a new Bible worksheet.
    
    Request Body:
        groupId: ID of the group
        title: Title of the worksheet
        content: Content of the worksheet (rich text or markdown)
    
    Returns:
        CreateWorksheetResponse with creation status and worksheet ID
    """
    controller = GroupsController()
    return await controller.create_worksheet(
        groupId=request.groupId,
        title=request.title,
        content=request.content
    )


@router.get("/get_worksheets", response_model=GetWorksheetsResponse)
async def get_worksheets(groupId: str = Query(..., description="ID of the group")):
    """
    Get all worksheets for a group.
    
    Query Parameters:
        groupId: ID of the group
    
    Returns:
        GetWorksheetsResponse with list of worksheets
    """
    controller = GroupsController()
    return await controller.get_group_worksheets(groupId=groupId)


@router.post("/upload_worksheet", response_model=UploadWorksheetResponse)
async def upload_worksheet(
    groupId: str = Form(...),
    title: str = Form(...),
    file: UploadFile = File(...)
):
    """
    Upload a worksheet file (PDF or DOCX) for a group.
    
    Form Parameters:
        groupId: ID of the group
        title: Title of the worksheet
        file: The worksheet file (PDF or DOCX)
    
    Returns:
        UploadWorksheetResponse with upload status and file information
    """
    controller = GroupsController()
    return await controller.upload_worksheet(
        groupId=groupId,
        title=title,
        file=file
    )


@router.get("/download_worksheet/{file_id}")
async def download_worksheet(file_id: str):
    """
    Download a worksheet file (public endpoint for PDF viewer).
    
    Path Parameters:
        file_id: ID of the file in GridFS
    
    Returns:
        StreamingResponse with the file
    
    Note: This endpoint does not require authentication to allow
    PDF viewers and download managers to access files.
    """
    controller = GroupsController()
    return await controller.download_worksheet_file(file_id)


@router.post("/create_worksheet_text", response_model=CreateWorksheetTextResponse)
async def create_worksheet_text(request: CreateWorksheetTextRequest):
    """
    Create a worksheet with HTML/text content (no file upload).
    
    Request Body:
        groupId: ID of the group
        title: Title of the worksheet
        content: HTML/text content of the worksheet
    
    Returns:
        CreateWorksheetTextResponse with creation status
    """
    controller = GroupsController()
    return await controller.create_worksheet_text(
        groupId=request.groupId,
        title=request.title,
        content=request.content
    )


@router.post("/join_group", response_model=JoinGroupResponse)
async def join_group(request: JoinGroupRequest):
    """
    Join a group.
    
    Request Body:
        groupId: ID of the group to join
        userId: ID of the user joining
    
    Returns:
        JoinGroupResponse with join status
    """
    controller = GroupsController()
    return await controller.join_group(
        groupId=request.groupId,
        userId=request.userId
    )


@router.post("/leave_group", response_model=LeaveGroupResponse)
async def leave_group(request: LeaveGroupRequest):
    """
    Leave a group.
    
    Request Body:
        groupId: ID of the group to leave
        userId: ID of the user leaving
    
    Returns:
        LeaveGroupResponse with leave status
    """
    controller = GroupsController()
    return await controller.leave_group(
        groupId=request.groupId,
        userId=request.userId
    )


@router.post("/create_group_request", response_model=CreateGroupRequestResponse)
async def create_group_request(request: CreateGroupRequestRequest):
    """
    Create a new group request.
    
    Request Body:
        groupId: ID of the group
        userId: ID of the user making the request
        requestMessage: Message from the user requesting to join
    
    Returns:
        CreateGroupRequestResponse with creation status and request ID
    """
    controller = GroupsController()
    return await controller.create_group_request(
        groupId=request.groupId,
        userId=request.userId,
        requestMessage=request.requestMessage
    )


@router.get("/get_group_requests", response_model=GetGroupRequestsResponse)
async def get_group_requests(groupId: str = Query(..., description="Group ID")):
    """
    Get all requests for a group.
    
    Query Parameters:
        groupId: ID of the group
    
    Returns:
        GetGroupRequestsResponse with list of group requests
    """
    controller = GroupsController()
    return await controller.get_group_requests(groupId=groupId)


@router.post("/create_group_role_config", response_model=CreateGroupRoleConfigResponse)
async def create_group_role_config(request: CreateGroupRoleConfigRequest):
    """
    Create a group-specific role configuration.
    
    Request Body:
        groupId: ID of the group
        roleName: Name of the role (e.g., "admin", "moderator")
        permissions: List of permission action strings
    
    Returns:
        CreateGroupRoleConfigResponse with creation status and group role ID
    """
    controller = GroupsController()
    return await controller.create_group_role_config(
        groupId=request.groupId,
        roleName=request.roleName,
        permissions=request.permissions
    )


@router.get("/get_group_role_configs", response_model=GetGroupRoleConfigsResponse)
async def get_group_role_configs(groupId: str = Query(..., description="Group ID")):
    """
    Get all role configurations for a group.
    
    Query Parameters:
        groupId: ID of the group
    
    Returns:
        GetGroupRoleConfigsResponse with list of group role configurations
    """
    controller = GroupsController()
    return await controller.get_group_role_configs(groupId=groupId)


@router.post("/update_group_role_config", response_model=UpdateGroupRoleConfigResponse)
async def update_group_role_config(request: UpdateGroupRoleConfigRequest):
    """
    Update a group role configuration.
    
    Request Body:
        groupId: ID of the group
        roleName: Name of the role to update
        permissions: New list of permission action strings
    
    Returns:
        UpdateGroupRoleConfigResponse with update status
    """
    controller = GroupsController()
    return await controller.update_group_role_config(
        groupId=request.groupId,
        roleName=request.roleName,
        permissions=request.permissions
    )


@router.post("/delete_group_role_config", response_model=DeleteGroupRoleConfigResponse)
async def delete_group_role_config(request: DeleteGroupRoleConfigRequest):
    """
    Delete a group role configuration.
    
    Request Body:
        groupId: ID of the group
        roleName: Name of the role to delete
    
    Returns:
        DeleteGroupRoleConfigResponse with deletion status
    """
    controller = GroupsController()
    return await controller.delete_group_role_config(
        groupId=request.groupId,
        roleName=request.roleName
    )
