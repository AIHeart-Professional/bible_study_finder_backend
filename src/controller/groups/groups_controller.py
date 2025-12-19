"""Groups controller - Business logic distributor layer."""
from typing import Optional
from fastapi import UploadFile, HTTPException
from fastapi.responses import StreamingResponse
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
    LeaveGroupResponse,
    CreateGroupRequestResponse,
    GetGroupRequestsResponse,
    GroupRoleConfig,
    CreateGroupRoleConfigResponse,
    GetGroupRoleConfigsResponse,
    UpdateGroupRoleConfigResponse,
    DeleteGroupRoleConfigResponse,
    UploadWorksheetResponse,
    CreateWorksheetTextResponse
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
    
    async def upload_worksheet(
        self,
        groupId: str,
        title: str,
        file: UploadFile
    ) -> UploadWorksheetResponse:
        """Upload a worksheet file."""
        try:
            result = await self.groups_service.upload_worksheet(
                groupId=groupId,
                title=title,
                file=file
            )
            
            return UploadWorksheetResponse(
                success=result[0],
                message=result[1],
                worksheetId=result[2],
                fileId=result[3],
                fileName=result[4],
                fileType=result[5]
            )
        except Exception as e:
            self.logger.error(f"Error in upload_worksheet controller: {e}")
            return UploadWorksheetResponse(
                success=False,
                message=f"Error uploading worksheet: {str(e)}",
                worksheetId=None,
                fileId=None,
                fileName=None,
                fileType=None
            )
    
    async def download_worksheet_file(self, file_id: str) -> StreamingResponse:
        """Download a worksheet file."""
        self.logger.debug(f"download_worksheet_file called with file_id={file_id}")
        try:
            file_data = await self.groups_service.get_worksheet_file(file_id)
            
            if not file_data:
                raise HTTPException(status_code=404, detail="File not found")
            
            return file_data
        except Exception as e:
            self.logger.error(f"Error downloading worksheet: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    
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
    
    async def create_group_request(
        self,
        groupId: str,
        userId: str,
        requestMessage: str
    ) -> CreateGroupRequestResponse:
        """Create a new group request."""
        try:
            self.logger.debug(f"create_group_request controller called with groupId={groupId}, userId={userId}")
            
            success, message, request_id = await self.groups_service.create_group_request(
                groupId=groupId,
                userId=userId,
                requestMessage=requestMessage
            )
            
            self.logger.info(f"Group request creation completed: success={success}")
            return CreateGroupRequestResponse(
                success=success,
                message=message,
                requestId=request_id
            )
        except Exception as e:
            self.logger.error(f"Error in create_group_request controller: {e}", exc_info=True)
            return CreateGroupRequestResponse(
                success=False,
                message=f"Error creating group request: {str(e)}",
                requestId=None
            )
    
    async def get_group_requests(self, groupId: str) -> GetGroupRequestsResponse:
        """Get all requests for a group."""
        try:
            self.logger.debug(f"get_group_requests controller called with groupId={groupId}")
            
            success, message, requests_data = await self.groups_service.get_group_requests(groupId=groupId)
            
            # Convert dict to GroupRequest models
            from src.models.groups import GroupRequest
            from datetime import datetime
            
            requests = []
            for req in requests_data:
                # Handle createdAt - it might be datetime or string
                created_at = req['createdAt']
                if isinstance(created_at, str):
                    try:
                        created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00').split('.')[0])
                    except:
                        created_at = datetime.utcnow()
                elif not isinstance(created_at, datetime):
                    created_at = datetime.utcnow()
                
                requests.append(
                    GroupRequest(
                        id=req['id'],
                        groupId=req['groupId'],
                        userId=req['userId'],
                        requestMessage=req['requestMessage'],
                        createdAt=created_at,
                        status=req.get('status', 'pending')
                    )
                )
            
            self.logger.info(f"Group requests retrieval completed: success={success}, count={len(requests)}")
            return GetGroupRequestsResponse(
                success=success,
                message=message,
                requests=requests
            )
        except Exception as e:
            self.logger.error(f"Error in get_group_requests controller: {e}", exc_info=True)
            return GetGroupRequestsResponse(
                success=False,
                message=f"Error getting group requests: {str(e)}",
                requests=[]
            )
    
    async def create_group_role_config(
        self,
        groupId: str,
        roleName: str,
        permissions: list
    ) -> CreateGroupRoleConfigResponse:
        """Create a group-specific role configuration."""
        try:
            self.logger.debug(f"create_group_role_config controller called with groupId={groupId}, roleName={roleName}")
            
            success, message, group_role_id = await self.groups_service.create_group_role_config(
                groupId=groupId,
                roleName=roleName,
                permissions=permissions
            )
            
            self.logger.info(f"Group role config creation completed: success={success}")
            return CreateGroupRoleConfigResponse(
                success=success,
                message=message,
                groupRoleId=group_role_id
            )
        except Exception as e:
            self.logger.error(f"Error in create_group_role_config controller: {e}", exc_info=True)
            return CreateGroupRoleConfigResponse(
                success=False,
                message=f"Error creating group role config: {str(e)}",
                groupRoleId=None
            )
    
    async def get_group_role_configs(self, groupId: str) -> GetGroupRoleConfigsResponse:
        """Get all role configurations for a group."""
        try:
            self.logger.debug(f"get_group_role_configs controller called with groupId={groupId}")
            
            success, message, configs_data = await self.groups_service.get_group_role_configs(groupId=groupId)
            
            configs = [
                GroupRoleConfig(
                    id=config['id'],
                    groupId=config['groupId'],
                    roleName=config['roleName'],
                    permissions=config['permissions']
                )
                for config in configs_data
            ]
            
            self.logger.info(f"Group role configs retrieval completed: success={success}, count={len(configs)}")
            return GetGroupRoleConfigsResponse(
                success=success,
                message=message,
                groupRoles=configs
            )
        except Exception as e:
            self.logger.error(f"Error in get_group_role_configs controller: {e}", exc_info=True)
            return GetGroupRoleConfigsResponse(
                success=False,
                message=f"Error getting group role configs: {str(e)}",
                groupRoles=[]
            )
    
    async def update_group_role_config(
        self,
        groupId: str,
        roleName: str,
        permissions: list
    ) -> UpdateGroupRoleConfigResponse:
        """Update a group role configuration."""
        try:
            self.logger.debug(f"update_group_role_config controller called with groupId={groupId}, roleName={roleName}")
            
            success, message = await self.groups_service.update_group_role_config(
                groupId=groupId,
                roleName=roleName,
                permissions=permissions
            )
            
            self.logger.info(f"Group role config update completed: success={success}")
            return UpdateGroupRoleConfigResponse(
                success=success,
                message=message
            )
        except Exception as e:
            self.logger.error(f"Error in update_group_role_config controller: {e}", exc_info=True)
            return UpdateGroupRoleConfigResponse(
                success=False,
                message=f"Error updating group role config: {str(e)}"
            )
    
    async def delete_group_role_config(
        self,
        groupId: str,
        roleName: str
    ) -> DeleteGroupRoleConfigResponse:
        """Delete a group role configuration."""
        try:
            self.logger.debug(f"delete_group_role_config controller called with groupId={groupId}, roleName={roleName}")
            
            success, message = await self.groups_service.delete_group_role_config(
                groupId=groupId,
                roleName=roleName
            )
            
            self.logger.info(f"Group role config deletion completed: success={success}")
            return DeleteGroupRoleConfigResponse(
                success=success,
                message=message
            )
        except Exception as e:
            self.logger.error(f"Error in delete_group_role_config controller: {e}", exc_info=True)
            return DeleteGroupRoleConfigResponse(
                success=False,
                message=f"Error deleting group role config: {str(e)}"
            )
    
    async def create_worksheet_text(
        self,
        groupId: str,
        title: str,
        content: str
    ) -> CreateWorksheetTextResponse:
        """Create a worksheet with HTML/text content."""
        try:
            self.logger.debug(f"create_worksheet_text controller called with groupId={groupId}, title={title}")
            
            success, message, worksheet_id = await self.groups_service.create_worksheet_text(
                groupId=groupId,
                title=title,
                content=content
            )
            
            self.logger.info(f"Worksheet creation completed: success={success}, worksheetId={worksheet_id}")
            return CreateWorksheetTextResponse(
                success=success,
                message=message,
                worksheetId=worksheet_id
            )
        except Exception as e:
            self.logger.error(f"Error in create_worksheet_text controller: {e}", exc_info=True)
            return CreateWorksheetTextResponse(
                success=False,
                message=f"Error creating worksheet: {str(e)}",
                worksheetId=None
            )
