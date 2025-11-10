"""Groups routes - HTTP layer."""
from fastapi import APIRouter, Query, Depends
from src.models.groups import (
    CreateGroupRequest,
    CreateGroupResponse,
    InitializeGroupRequest,
    InitializeGroupResponse,
    GetUsersRequest,
    GetUsersResponse,
    GetChatRequest,
    GetChatResponse,
    GetMealsRequest,
    GetMealsResponse,
    GetStudyPlanRequest,
    GetStudyPlanResponse,
    GetGroupsResponse,
    GetGroupResponse,
    CreateGroupChatRequest,
    CreateGroupChatResponse,
    CreateWorksheetRequest,
    CreateWorksheetResponse,
    GetWorksheetsRequest,
    GetWorksheetsResponse,
    JoinGroupRequest,
    JoinGroupResponse,
    LeaveGroupRequest,
    LeaveGroupResponse
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
async def get_users(request: GetUsersRequest):
    """
    Get all users (members) of a group.
    
    Query Parameters:
        groupId: ID of the group
    
    Returns:
        GetUsersResponse with list of group members
    """
    controller = GroupsController()
    return await controller.get_group_users(groupId=request.groupId)


@router.get("/get_chat", response_model=GetChatResponse)
async def get_chat(request: GetChatRequest = Depends()):
    """
    Get all chat messages for a group.
    
    Query Parameters:
        groupId: ID of the group
    
    Returns:
        GetChatResponse with list of chat messages
    """
    controller = GroupsController()
    return await controller.get_group_chat(groupId=request.groupId)


@router.get("/get_meals", response_model=GetMealsResponse)
async def get_meals(request: GetMealsRequest):
    """
    Get all meals for a group.
    
    Query Parameters:
        groupId: ID of the group
    
    Returns:
        GetMealsResponse with list of meals
    """
    controller = GroupsController()
    return await controller.get_group_meals(groupId=request.groupId)


@router.get("/get_study_plan", response_model=GetStudyPlanResponse)
async def get_study_plan(request: GetStudyPlanRequest):
    """
    Get all study plans for a group.
    
    Query Parameters:
        groupId: ID of the group
    
    Returns:
        GetStudyPlanResponse with list of study plans
    """
    controller = GroupsController()
    return await controller.get_group_study_plans(groupId=request.groupId)


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
async def get_worksheets(request: GetWorksheetsRequest = Depends()):
    """
    Get all worksheets for a group.
    
    Query Parameters:
        groupId: ID of the group
    
    Returns:
        GetWorksheetsResponse with list of worksheets
    """
    controller = GroupsController()
    return await controller.get_group_worksheets(groupId=request.groupId)


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
