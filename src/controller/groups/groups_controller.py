"""Groups controller - Business logic distributor layer."""
from typing import Optional
from src.models.groups import (
    CreateGroupResponse,
    InitializeGroupResponse,
    GetUsersResponse,
    GetChatResponse,
    GetMealsResponse,
    GetStudyPlanResponse,
    GetGroupsResponse,
    GetGroupResponse,
    CreateGroupChatResponse,
    CreateWorksheetResponse,
    GetWorksheetsResponse,
    JoinGroupResponse,
    LeaveGroupResponse
)
from src.utils.logger import get_logger
from src.services.groups_service import GroupsService

class GroupsController:
    """Controller for handling group business logic."""
    
    def __init__(self):
        """Initialize the controller and groups service."""
        self.groups_service = GroupsService()
        self.logger = get_logger(__name__)
    
    async def create_group(
        self,
        name: str,
        description: str,
        leaderUserId: str,
        location: dict,
        image: Optional[str] = None
    ) -> CreateGroupResponse:
        """Create a new group."""
        try:
            success, message, group_id = await self.groups_service.create_group(
                name=name,
                description=description,
                leaderUserId=leaderUserId,
                location=location,
                image=image
            )
            
            return CreateGroupResponse(
                success=success,
                message=message,
                groupId=group_id
            )
        except Exception as e:
            self.logger.error(f"Error in create_group controller: {e}")
            return CreateGroupResponse(
                success=False,
                message=f"Error creating group: {str(e)}",
                groupId=None
            )
    
    async def initialize_group(self, groupId: str) -> InitializeGroupResponse:
        """Initialize a group."""
        try:
            success, message = await self.groups_service.initialize_group(groupId)
            
            return InitializeGroupResponse(
                success=success,
                message=message
            )
        except Exception as e:
            self.logger.error(f"Error in initialize_group controller: {e}")
            return InitializeGroupResponse(
                success=False,
                message=f"Error initializing group: {str(e)}"
            )
    
    async def get_group_users(self, groupId: str) -> GetUsersResponse:
        """Get all users in a group."""
        try:
            success, message, users, member_count = await self.groups_service.get_group_users(groupId)
            
            return GetUsersResponse(
                success=success,
                message=message,
                users=users,
                memberCount=member_count
            )
        except Exception as e:
            self.logger.error(f"Error in get_group_users controller: {e}")
            return GetUsersResponse(
                success=False,
                message=f"Error getting group users: {str(e)}",
                users=[],
                memberCount=0
            )
    
    async def get_group_chat(self, groupId: str) -> GetChatResponse:
        """Get all chat messages for a group."""
        try:
            success, message, messages = await self.groups_service.get_group_chat(groupId)
            
            return GetChatResponse(
                success=success,
                message=message,
                messages=messages
            )
        except Exception as e:
            self.logger.error(f"Error in get_group_chat controller: {e}")
            return GetChatResponse(
                success=False,
                message=f"Error getting group chat: {str(e)}",
                messages=[]
            )
    
    async def get_group_meals(self, groupId: str) -> GetMealsResponse:
        """Get all meals for a group."""
        try:
            success, message, meals = await self.groups_service.get_group_meals(groupId)
            
            return GetMealsResponse(
                success=success,
                message=message,
                meals=meals
            )
        except Exception as e:
            self.logger.error(f"Error in get_group_meals controller: {e}")
            return GetMealsResponse(
                success=False,
                message=f"Error getting group meals: {str(e)}",
                meals=[]
            )
    
    async def get_group_study_plans(self, groupId: str) -> GetStudyPlanResponse:
        """Get all study plans for a group."""
        try:
            success, message, study_plans = await self.groups_service.get_group_study_plans(groupId)
            
            return GetStudyPlanResponse(
                success=success,
                message=message,
                studyPlans=study_plans
            )
        except Exception as e:
            self.logger.error(f"Error in get_group_study_plans controller: {e}")
            return GetStudyPlanResponse(
                success=False,
                message=f"Error getting group study plans: {str(e)}",
                studyPlans=[]
            )
    
    async def get_all_groups(self) -> GetGroupsResponse:
        """Get all groups."""
        try:
            success, message, groups = await self.groups_service.get_all_groups()
            
            return GetGroupsResponse(
                success=success,
                message=message,
                groups=groups
            )
        except Exception as e:
            self.logger.error(f"Error in get_all_groups controller: {e}")
            return GetGroupsResponse(
                success=False,
                message=f"Error getting all groups: {str(e)}",
                groups=[]
            )
    
    async def get_group(self, groupId: str) -> GetGroupResponse:
        """Get a single group by ID."""
        try:
            success, message, group = await self.groups_service.get_group(groupId)
            
            return GetGroupResponse(
                success=success,
                message=message,
                group=group
            )
        except Exception as e:
            self.logger.error(f"Error in get_group controller: {e}")
            return GetGroupResponse(
                success=False,
                message=f"Error getting group: {str(e)}",
                group=None
            )
    
    async def get_groups_by_user_id(self, userId: str) -> GetGroupsResponse:
        """Get all groups that a user is a member of."""
        try:
            success, message, groups = await self.groups_service.get_groups_by_user_id(userId)
            
            return GetGroupsResponse(
                success=success,
                message=message,
                groups=groups
            )
        except Exception as e:
            self.logger.error(f"Error in get_groups_by_user_id controller: {e}")
            return GetGroupsResponse(
                success=False,
                message=f"Error getting user groups: {str(e)}",
                groups=[]
            )
    
    async def create_group_chat(
        self,
        groupId: str,
        userId: str,
        message: str
    ) -> CreateGroupChatResponse:
        """Create a new group chat message."""
        try:
            success, msg, chat_id = await self.groups_service.create_group_chat(
                groupId=groupId,
                userId=userId,
                message=message
            )
            
            return CreateGroupChatResponse(
                success=success,
                message=msg,
                chatId=chat_id
            )
        except Exception as e:
            self.logger.error(f"Error in create_group_chat controller: {e}")
            return CreateGroupChatResponse(
                success=False,
                message=f"Error creating group chat: {str(e)}",
                chatId=None
            )
    
    async def create_worksheet(
        self,
        groupId: str,
        title: str,
        content: str
    ) -> CreateWorksheetResponse:
        """Create a new Bible worksheet."""
        try:
            success, msg, worksheet_id = await self.groups_service.create_worksheet(
                groupId=groupId,
                title=title,
                content=content
            )
            
            return CreateWorksheetResponse(
                success=success,
                message=msg,
                worksheetId=worksheet_id
            )
        except Exception as e:
            self.logger.error(f"Error in create_worksheet controller: {e}")
            return CreateWorksheetResponse(
                success=False,
                message=f"Error creating worksheet: {str(e)}",
                worksheetId=None
            )
    
    async def get_group_worksheets(self, groupId: str) -> GetWorksheetsResponse:
        """Get all worksheets for a group."""
        try:
            success, message, worksheets = await self.groups_service.get_group_worksheets(groupId)
            
            return GetWorksheetsResponse(
                success=success,
                message=message,
                worksheets=worksheets
            )
        except Exception as e:
            self.logger.error(f"Error in get_group_worksheets controller: {e}")
            return GetWorksheetsResponse(
                success=False,
                message=f"Error getting group worksheets: {str(e)}",
                worksheets=[]
            )
    
    async def join_group(
        self,
        groupId: str,
        userId: str
    ) -> JoinGroupResponse:
        """Join a group."""
        try:
            success, message = await self.groups_service.join_group(
                groupId=groupId,
                userId=userId
            )
            
            return JoinGroupResponse(
                success=success,
                message=message
            )
        except Exception as e:
            self.logger.error(f"Error in join_group controller: {e}")
            return JoinGroupResponse(
                success=False,
                message=f"Error joining group: {str(e)}"
            )
    
    async def leave_group(
        self,
        groupId: str,
        userId: str
    ) -> LeaveGroupResponse:
        """Leave a group."""
        try:
            success, message = await self.groups_service.leave_group(
                groupId=groupId,
                userId=userId
            )
            
            return LeaveGroupResponse(
                success=success,
                message=message
            )
        except Exception as e:
            self.logger.error(f"Error in leave_group controller: {e}")
            return LeaveGroupResponse(
                success=False,
                message=f"Error leaving group: {str(e)}"
            )
