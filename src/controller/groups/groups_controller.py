"""Groups controller - Business logic distributor layer (BIGINT IDs)."""
from typing import Optional, List
from fastapi import UploadFile, HTTPException
from fastapi.responses import StreamingResponse
from src.models.groups import (
    CreateGroupResponse,
    InitializeGroupResponse,
    GetUsersResponse,
    GetGroupChatResponse,
    GetMealsResponse,
    GetStudyPlanResponse,
    GetGroupsResponse,
    GetGroupResponse,
    CreateGroupChatResponse,
    CreateWorksheetResponse,
    GetWorksheetsResponse,
    JoinGroupResponse,
    LeaveGroupResponse,
    CreateGroupRequestResponse,
    GetGroupRequestsResponse,
    GroupRoleConfig,
    CreateGroupRoleConfigResponse,
    GetGroupRoleConfigsResponse,
    UpdateGroupRoleConfigResponse,
    DeleteGroupRoleConfigResponse,
    UploadWorksheetResponse,
    CreateWorksheetTextResponse,
    GroupRequest
)
from src.utils.logger import get_logger
from src.services.groups_service import GroupsService

class GroupsController:
    """Controller for handling group business logic with BIGINT IDs."""
    
    def __init__(self):
        """Initialize the controller and groups service."""
        self.groups_service = GroupsService()
        self.logger = get_logger(__name__)
    
    async def create_group(
        self,
        name: str,
        description: str,
        leaderPublicId: str,
        location: dict,
        image: Optional[str] = None
    ) -> CreateGroupResponse:
        """Create a new group."""
        try:
            success, message, group_id = await self.groups_service.create_group(
                name=name,
                description=description,
                leaderPublicId=leaderPublicId,
                location=location,
                image=image
            )
            return CreateGroupResponse(success=success, message=message, groupPublicId=group_id)
        except Exception as e:
            self.logger.error(f"Error in create_group controller: {e}")
            return CreateGroupResponse(success=False, message=f"Error creating group: {str(e)}")
    
    async def initialize_group(self, groupPublicId: str) -> InitializeGroupResponse:
        """Initialize a group."""
        try:
            success, message = await self.groups_service.initialize_group(groupPublicId)
            return InitializeGroupResponse(success=success, message=message)
        except Exception as e:
            self.logger.error(f"Error in initialize_group controller: {e}")
            return InitializeGroupResponse(success=False, message=f"Error initializing group: {str(e)}")
    
    async def get_group_users(self, groupPublicId: str) -> GetUsersResponse:
        """Get all users in a group."""
        try:
            success, message, users, member_count = await self.groups_service.get_group_users(groupPublicId)
            return GetUsersResponse(success=success, message=message, users=users, memberCount=member_count)
        except Exception as e:
            self.logger.error(f"Error in get_group_users controller: {e}")
            return GetUsersResponse(success=False, message=f"Error getting group users: {str(e)}")
    
    async def get_group_chat(self, groupPublicId: str) -> GetGroupChatResponse:
        """Get all chat messages for a group."""
        try:
            success, message, messages = await self.groups_service.get_group_chat(groupPublicId)
            return GetGroupChatResponse(success=success, message=message, messages=messages)
        except Exception as e:
            self.logger.error(f"Error in get_group_chat controller: {e}")
            return GetGroupChatResponse(success=False, message=f"Error getting group chat: {str(e)}")
    
    async def get_group_meals(self, groupPublicId: str) -> GetMealsResponse:
        """Get all meals for a group."""
        try:
            success, message, meals = await self.groups_service.get_group_meals(groupPublicId)
            return GetMealsResponse(success=success, message=message, meals=meals)
        except Exception as e:
            self.logger.error(f"Error in get_group_meals controller: {e}")
            return GetMealsResponse(success=False, message=f"Error getting group meals: {str(e)}")
    
    async def get_group_study_plans(self, groupPublicId: str) -> GetStudyPlanResponse:
        """Get all study plans for a group."""
        try:
            success, message, study_plans = await self.groups_service.get_group_study_plans(groupPublicId)
            return GetStudyPlanResponse(success=success, message=message, studyPlans=study_plans)
        except Exception as e:
            self.logger.error(f"Error in get_group_study_plans controller: {e}")
            return GetStudyPlanResponse(success=False, message=f"Error getting group study plans: {str(e)}")
    
    async def get_all_groups(self) -> GetGroupsResponse:
        """Get all groups."""
        try:
            success, message, groups = await self.groups_service.get_all_groups()
            return GetGroupsResponse(success=success, message=message, groups=groups)
        except Exception as e:
            self.logger.error(f"Error in get_all_groups controller: {e}")
            return GetGroupsResponse(success=False, message=f"Error getting all groups: {str(e)}")
    
    async def get_group(self, groupPublicId: str) -> GetGroupResponse:
        """Get a single group by public_id (UUID)."""
        try:
            success, message, group = await self.groups_service.get_group(groupPublicId)
            return GetGroupResponse(success=success, message=message, group=group)
        except Exception as e:
            self.logger.error(f"Error in get_group controller: {e}")
            return GetGroupResponse(success=False, message=f"Error getting group: {str(e)}")
    
    async def get_groups_by_user_id(self, userPublicId: str) -> GetGroupsResponse:
        """Get all groups that a user is a member of."""
        try:
            success, message, groups = await self.groups_service.get_groups_by_user_id(userPublicId)
            return GetGroupsResponse(success=success, message=message, groups=groups)
        except Exception as e:
            self.logger.error(f"Error in get_groups_by_user_id controller: {e}")
            return GetGroupsResponse(success=False, message=f"Error getting user groups: {str(e)}")
    
    async def create_group_chat(self, groupPublicId: str, userPublicId: str, message: str) -> CreateGroupChatResponse:
        """Create a new group chat message."""
        try:
            success, msg, chat_id = await self.groups_service.create_group_chat(groupPublicId, userPublicId, message)
            return CreateGroupChatResponse(success=success, message=msg, chatId=chat_id)
        except Exception as e:
            self.logger.error(f"Error in create_group_chat controller: {e}")
            return CreateGroupChatResponse(success=False, message=f"Error creating group chat: {str(e)}")
    
    async def create_worksheet(self, groupPublicId: str, title: str, content: str) -> CreateWorksheetResponse:
        """Create a new Bible worksheet."""
        try:
            success, msg, worksheet_id = await self.groups_service.create_worksheet(groupPublicId, title, content)
            return CreateWorksheetResponse(success=success, message=msg, worksheetId=worksheet_id)
        except Exception as e:
            self.logger.error(f"Error in create_worksheet controller: {e}")
            return CreateWorksheetResponse(success=False, message=f"Error creating worksheet: {str(e)}")
    
    async def get_group_worksheets(self, groupPublicId: str) -> GetWorksheetsResponse:
        """Get all worksheets for a group."""
        try:
            success, message, worksheets = await self.groups_service.get_group_worksheets(groupPublicId)
            return GetWorksheetsResponse(success=success, message=message, worksheets=worksheets)
        except Exception as e:
            self.logger.error(f"Error in get_group_worksheets controller: {e}")
            return GetWorksheetsResponse(success=False, message=f"Error getting group worksheets: {str(e)}")
    
    async def upload_worksheet(self, groupPublicId: str, title: str, file: UploadFile) -> UploadWorksheetResponse:
        """Upload a worksheet file."""
        try:
            result = await self.groups_service.upload_worksheet(groupPublicId, title, file)
            return UploadWorksheetResponse(success=result[0], message=result[1], worksheetId=result[2], fileId=result[3], fileName=result[4], fileType=result[5])
        except Exception as e:
            self.logger.error(f"Error in upload_worksheet controller: {e}")
            return UploadWorksheetResponse(success=False, message=f"Error uploading worksheet: {str(e)}")
    
    async def download_worksheet_file(self, file_id: int) -> StreamingResponse:
        """Download a worksheet file."""
        try:
            file_data = await self.groups_service.get_worksheet_file(file_id)
            if not file_data: raise HTTPException(status_code=404, detail="File not found")
            return file_data
        except Exception as e:
            self.logger.error(f"Error downloading worksheet: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    
    async def join_group(self, groupPublicId: str, userPublicId: str) -> JoinGroupResponse:
        """Join a group."""
        try:
            success, message = await self.groups_service.join_group(groupPublicId, userPublicId)
            return JoinGroupResponse(success=success, message=message)
        except Exception as e:
            self.logger.error(f"Error in join_group controller: {e}")
            return JoinGroupResponse(success=False, message=f"Error joining group: {str(e)}")
    
    async def leave_group(self, groupPublicId: str, userPublicId: str) -> LeaveGroupResponse:
        """Leave a group."""
        try:
            success, message = await self.groups_service.leave_group(groupPublicId, userPublicId)
            return LeaveGroupResponse(success=success, message=message)
        except Exception as e:
            self.logger.error(f"Error in leave_group controller: {e}")
            return LeaveGroupResponse(success=False, message=f"Error leaving group: {str(e)}")
    
    async def create_group_request(self, groupPublicId: str, userPublicId: str, requestMessage: str) -> CreateGroupRequestResponse:
        """Create a new group request."""
        try:
            success, message, request_id = await self.groups_service.create_group_request(groupPublicId, userPublicId, requestMessage)
            return CreateGroupRequestResponse(success=success, message=message, requestId=request_id)
        except Exception as e:
            self.logger.error(f"Error in create_group_request controller: {e}")
            return CreateGroupRequestResponse(success=False, message=f"Error creating group request: {str(e)}")
    
    async def get_group_requests(self, groupPublicId: str) -> GetGroupRequestsResponse:
        """Get all requests for a group."""
        try:
            success, message, requests_data = await self.groups_service.get_group_requests(groupPublicId)
            requests = [GroupRequest(**req) for req in requests_data]
            return GetGroupRequestsResponse(success=success, message=message, requests=requests)
        except Exception as e:
            self.logger.error(f"Error in get_group_requests controller: {e}")
            return GetGroupRequestsResponse(success=False, message=f"Error getting group requests: {str(e)}")
    
    async def create_group_role_config(self, groupPublicId: str, roleName: str, permissions: list) -> CreateGroupRoleConfigResponse:
        """Create a group role configuration."""
        try:
            success, message, group_role_id = await self.groups_service.create_group_role_config(groupPublicId, roleName, permissions)
            return CreateGroupRoleConfigResponse(success=success, message=message, groupRoleId=group_role_id)
        except Exception as e:
            self.logger.error(f"Error in create_group_role_config controller: {e}")
            return CreateGroupRoleConfigResponse(success=False, message=f"Error creating group role config: {str(e)}")
    
    async def get_group_role_configs(self, groupPublicId: str) -> GetGroupRoleConfigsResponse:
        """Get all role configurations for a group."""
        try:
            success, message, configs_data = await self.groups_service.get_group_role_configs(groupPublicId)
            configs = [GroupRoleConfig(**config) for config in configs_data]
            return GetGroupRoleConfigsResponse(success=success, message=message, groupRoles=configs)
        except Exception as e:
            self.logger.error(f"Error in get_group_role_configs controller: {e}")
            return GetGroupRoleConfigsResponse(success=False, message=f"Error getting group role configs: {str(e)}")
    
    async def update_group_role_config(self, groupPublicId: str, roleName: str, permissions: list) -> UpdateGroupRoleConfigResponse:
        """Update a group role configuration."""
        try:
            success, message = await self.groups_service.update_group_role_config(groupPublicId, roleName, permissions)
            return UpdateGroupRoleConfigResponse(success=success, message=message)
        except Exception as e:
            self.logger.error(f"Error in update_group_role_config controller: {e}")
            return UpdateGroupRoleConfigResponse(success=False, message=f"Error updating group role config: {str(e)}")
    
    async def delete_group_role_config(self, groupPublicId: str, roleName: str) -> DeleteGroupRoleConfigResponse:
        """Delete a group role configuration."""
        try:
            success, message = await self.groups_service.delete_group_role_config(groupPublicId, roleName)
            return DeleteGroupRoleConfigResponse(success=success, message=message)
        except Exception as e:
            self.logger.error(f"Error in delete_group_role_config controller: {e}")
            return DeleteGroupRoleConfigResponse(success=False, message=f"Error deleting group role config: {str(e)}")
    
    async def create_worksheet_text(self, groupPublicId: str, title: str, content: str) -> CreateWorksheetTextResponse:
        """Create a worksheet with HTML/text content."""
        try:
            success, message, worksheet_id = await self.groups_service.create_worksheet_text(groupPublicId, title, content)
            return CreateWorksheetTextResponse(success=success, message=message, worksheetId=worksheet_id)
        except Exception as e:
            self.logger.error(f"Error in create_worksheet_text controller: {e}")
            return CreateWorksheetTextResponse(success=False, message=f"Error creating worksheet: {str(e)}")
