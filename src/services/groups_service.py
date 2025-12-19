"""Groups service - Application logic layer."""
from typing import List, Optional
from datetime import datetime
from fastapi import UploadFile
from src.models.groups import (
    GroupMember,
    ChatMessage,
    Meal,
    StudyPlan,
    Group,
    Location,
    Worksheet
)
from src.utils.logger import get_logger
from src.database.groups.groups_database import GroupsDatabase
from src.database.users.users_database import UsersDatabase
from src.services.notification_service import NotificationService

class GroupsService:
    """Service for handling group business logic."""
    
    def __init__(self):
        """Initialize the service and database."""
        self.logger = get_logger(__name__)
        self.groups_database = GroupsDatabase()
        self.users_database = UsersDatabase()
        self.notification_service = NotificationService()
        self.logger.info("GroupsService initialized successfully")
    
    def _parse_datetime(self, dt_value) -> datetime:
        """Parse datetime value to datetime object."""
        if isinstance(dt_value, datetime):
            return dt_value
        if isinstance(dt_value, str):
            return datetime.fromisoformat(dt_value.replace('Z', '+00:00').split('.')[0])
        return datetime.utcnow()
    
    def _convert_location(self, location_data: dict) -> dict:
        """Convert location data to proper format."""
        return {
            'address': location_data.get('address'),
            'city': location_data.get('city'),
            'state': location_data.get('state'),
            'country': location_data.get('country'),
            'zipcode': location_data.get('zipcode'),
            'latitude': location_data.get('latitude'),
            'longitude': location_data.get('longitude'),
            'virtualMeetingLink': location_data.get('virtualMeetingLink')
        }
    
    async def create_group(
        self,
        name: str,
        description: str,
        leaderUserId: str,
        location: dict,
        image: Optional[str] = None
    ) -> tuple[bool, str, Optional[str]]:
        """Create a new group."""
        try:
            location_dict = self._convert_location(location)
            group_id = await self.groups_database.create_group(
                name=name,
                description=description,
                leaderUserId=leaderUserId,
                location=location_dict,
                image=image
            )
            
            if group_id:
                self.logger.info(f"Group created successfully: {group_id}")
                return True, "Group created successfully", group_id
            else:
                return False, "Failed to create group", None
                
        except Exception as e:
            self.logger.error(f"Error creating group: {e}")
            return False, f"Error creating group: {str(e)}", None
    
    async def initialize_group(self, groupId: str) -> tuple[bool, str]:
        """Initialize a group with empty arrays."""
        try:
            group = await self.groups_database.get_group_by_id(groupId)
            if not group:
                return False, "Group not found"
            
            success = await self.groups_database.initialize_group(groupId)
            if success:
                return True, "Group initialized successfully"
            else:
                return False, "Failed to initialize group"
                
        except Exception as e:
            self.logger.error(f"Error initializing group: {e}")
            return False, f"Error initializing group: {str(e)}"
    
    def _get_member_data(self, membership: dict, user: dict) -> GroupMember:
        """Convert membership and user data to GroupMember model."""
        return GroupMember(
            userId=str(user['id']),
            username=user.get('username', ''),
            email=user.get('email', ''),
            portraitUrl=user.get('portraitUrl'),
            role=membership.get('role', 'member'),
            joinedAt=self._parse_datetime(membership.get('joinedAt'))
        )
    
    async def get_group_users(self, groupId: str) -> tuple[bool, str, List[GroupMember], int]:
        """Get all users in a group."""
        try:
            group = await self.groups_database.get_group_by_id(groupId)
            if not group:
                return False, "Group not found", [], 0
            
            memberships = await self.groups_database.get_group_members(groupId)
            members = []
            
            for membership in memberships:
                user = await self.groups_database.get_user_by_id(membership['userId'])
                if user:
                    members.append(self._get_member_data(membership, user))
            
            member_count = len(members)
            return True, "Users retrieved successfully", members, member_count
            
        except Exception as e:
            self.logger.error(f"Error getting group users: {e}")
            return False, f"Error getting group users: {str(e)}", [], 0
    
    def _convert_chat_to_message(self, chat: dict, user: dict) -> ChatMessage:
        """Convert chat and user data to ChatMessage model."""
        return ChatMessage(
            id=chat['id'],
            userId=str(user['id']),
            username=user.get('username', ''),
            message=chat.get('message', ''),
            sentAt=self._parse_datetime(chat.get('sentAt'))
        )
    
    async def get_group_chat(self, groupId: str) -> tuple[bool, str, List[ChatMessage]]:
        """Get all chat messages for a group."""
        try:
            group = await self.groups_database.get_group_by_id(groupId)
            if not group:
                return False, "Group not found", []
            
            chats = await self.groups_database.get_group_chats(groupId)
            messages = []
            
            for chat in chats:
                user = await self.groups_database.get_user_by_id(chat['userId'])
                if user:
                    messages.append(self._convert_chat_to_message(chat, user))
            
            return True, "Chat messages retrieved successfully", messages
            
        except Exception as e:
            self.logger.error(f"Error getting group chat: {e}")
            return False, f"Error getting group chat: {str(e)}", []
    
    def _convert_meal_data_to_meal(self, meal_data: dict) -> Meal:
        """Convert meal data to Meal model."""
        return Meal(
            id=str(meal_data.get('_id', meal_data.get('id', ''))),
            mealName=meal_data.get('mealName', ''),
            description=meal_data.get('description', ''),
            createdAt=self._parse_datetime(meal_data.get('createdAt'))
        )
    
    async def get_group_meals(self, groupId: str) -> tuple[bool, str, List[Meal]]:
        """Get all meals for a group."""
        try:
            group = await self.groups_database.get_group_by_id(groupId)
            if not group:
                return False, "Group not found", []
            
            meals_data = await self.groups_database.get_group_meals(groupId)
            meals = [self._convert_meal_data_to_meal(meal_data) for meal_data in meals_data]
            
            return True, "Meals retrieved successfully", meals
            
        except Exception as e:
            self.logger.error(f"Error getting group meals: {e}")
            return False, f"Error getting group meals: {str(e)}", []
    
    def _convert_plan_data_to_plan(self, plan_data: dict) -> StudyPlan:
        """Convert plan data to StudyPlan model."""
        return StudyPlan(
            id=str(plan_data.get('_id', plan_data.get('id', ''))),
            title=plan_data.get('title', ''),
            description=plan_data.get('description', ''),
            createdAt=self._parse_datetime(plan_data.get('createdAt'))
        )
    
    async def get_group_study_plans(self, groupId: str) -> tuple[bool, str, List[StudyPlan]]:
        """Get all study plans for a group."""
        try:
            group = await self.groups_database.get_group_by_id(groupId)
            if not group:
                return False, "Group not found", []
            
            study_plans_data = await self.groups_database.get_group_study_plans(groupId)
            study_plans = [self._convert_plan_data_to_plan(plan_data) for plan_data in study_plans_data]
            
            return True, "Study plans retrieved successfully", study_plans
            
        except Exception as e:
            self.logger.error(f"Error getting group study plans: {e}")
            return False, f"Error getting group study plans: {str(e)}", []
    
    def _convert_group_data_to_group(self, group_data: dict) -> Group:
        """Convert group data to Group model."""
        location = Location(**group_data.get('location', {}))
        return Group(
            id=group_data['id'],
            name=group_data.get('name', ''),
            description=group_data.get('description', ''),
            leaderUserId=str(group_data.get('leaderUserId', '')),
            location=location,
            image=group_data.get('image'),
            createdAt=self._parse_datetime(group_data.get('createdAt')),
            updatedAt=self._parse_datetime(group_data.get('updatedAt'))
        )
    
    async def get_all_groups(self) -> tuple[bool, str, List[Group]]:
        """Get all groups."""
        try:
            groups_data = await self.groups_database.get_all_groups()
            groups = [self._convert_group_data_to_group(group_data) for group_data in groups_data]
            return True, "Groups retrieved successfully", groups
        except Exception as e:
            self.logger.error(f"Error getting all groups: {e}")
            return False, f"Error getting all groups: {str(e)}", []
    
    async def get_group(self, groupId: str) -> tuple[bool, str, Optional[Group]]:
        """Get a single group by ID."""
        try:
            group_data = await self.groups_database.get_group_by_id(groupId)
            if not group_data:
                return False, "Group not found", None
            
            group = self._convert_group_data_to_group(group_data)
            return True, "Group retrieved successfully", group
        except Exception as e:
            self.logger.error(f"Error getting group: {e}")
            return False, f"Error getting group: {str(e)}", None
    
    async def get_groups_by_user_id(self, userId: str) -> tuple[bool, str, List[Group]]:
        """Get all groups that a user is a member of."""
        try:
            groups_data = await self.groups_database.get_groups_by_user_id(userId)
            groups = [self._convert_group_data_to_group(group_data) for group_data in groups_data]
            return True, "User groups retrieved successfully", groups
        except Exception as e:
            self.logger.error(f"Error getting groups by user ID: {e}")
            return False, f"Error getting user groups: {str(e)}", []
    
    async def create_group_chat(
        self,
        groupId: str,
        userId: str,
        message: str
    ) -> tuple[bool, str, Optional[str]]:
        """Create a new group chat message."""
        try:
            group = await self.groups_database.get_group_by_id(groupId)
            if not group:
                return False, "Group not found", None
            
            chat_id = await self.groups_database.create_group_chat(
                groupId=groupId,
                userId=userId,
                message=message
            )
            
            if chat_id:
                self.logger.info(f"Group chat created successfully: {chat_id}")
                await self._send_chat_notifications(groupId, userId, message, group)
                return True, "Group chat created successfully", chat_id
            else:
                return False, "Failed to create group chat", None
                
        except Exception as e:
            self.logger.error(f"Error creating group chat: {e}")
            return False, f"Error creating group chat: {str(e)}", None
    
    async def _send_chat_notifications(
        self,
        groupId: str,
        senderUserId: str,
        message: str,
        group: dict
    ):
        """Send push notifications to group members when a new chat message is posted."""
        try:
            self.logger.debug(f"Sending chat notifications for group: {groupId}")
            
            # Get all group members
            members = await self.groups_database.get_group_members(groupId)
            if not members:
                self.logger.debug("No members found for group")
                return
            
            # Get recipient user IDs (excluding sender)
            recipient_ids = [
                member['userId'] 
                for member in members 
                if member.get('userId') != senderUserId
            ]
            
            if not recipient_ids:
                self.logger.debug("No recipients for notification")
                return
            
            # Get FCM tokens for recipients
            fcm_tokens = await self.users_database.get_fcm_tokens_for_users(recipient_ids)
            
            if not fcm_tokens:
                self.logger.debug("No FCM tokens found for recipients")
                return
            
            # Get sender username
            sender = await self.users_database.get_user_by_id(senderUserId)
            sender_username = sender.get('username', 'Someone') if sender else 'Someone'
            
            # Get group name
            group_name = group.get('name', 'Group') if group else 'Group'
            
            # Send notifications
            await self.notification_service.send_group_chat_notification(
                group_id=groupId,
                group_name=group_name,
                sender_username=sender_username,
                message=message,
                recipient_user_ids=recipient_ids,
                fcm_tokens=fcm_tokens
            )
            
        except Exception as e:
            self.logger.error(f"Error sending chat notifications: {e}", exc_info=True)
            # Don't fail the chat creation if notification fails
    
    async def create_worksheet(
        self,
        groupId: str,
        title: str,
        content: str
    ) -> tuple[bool, str, Optional[str]]:
        """Create a new Bible worksheet."""
        try:
            group = await self.groups_database.get_group_by_id(groupId)
            if not group:
                return False, "Group not found", None
            
            worksheet_id = await self.groups_database.create_worksheet(
                groupId=groupId,
                title=title,
                content=content
            )
            
            if worksheet_id:
                self.logger.info(f"Worksheet created successfully: {worksheet_id}")
                return True, "Worksheet created successfully", worksheet_id
            else:
                return False, "Failed to create worksheet", None
                
        except Exception as e:
            self.logger.error(f"Error creating worksheet: {e}")
            return False, f"Error creating worksheet: {str(e)}", None
    
    def _convert_worksheet_data_to_worksheet(self, worksheet_data: dict) -> Worksheet:
        """Convert worksheet data to Worksheet model."""
        return Worksheet(
            id=worksheet_data['id'],
            groupId=str(worksheet_data.get('groupId', '')),
            title=worksheet_data.get('title', ''),
            content=worksheet_data.get('content', ''),
            createdAt=self._parse_datetime(worksheet_data.get('createdAt')),
            updatedAt=self._parse_datetime(worksheet_data.get('updatedAt'))
        )
    
    async def get_group_worksheets(self, groupId: str) -> tuple[bool, str, List[Worksheet]]:
        """Get all worksheets for a group."""
        try:
            group = await self.groups_database.get_group_by_id(groupId)
            if not group:
                return False, "Group not found", []
            
            worksheets_data = await self.groups_database.get_group_worksheets(groupId)
            worksheets = [self._convert_worksheet_data_to_worksheet(ws_data) for ws_data in worksheets_data]
            
            return True, "Worksheets retrieved successfully", worksheets
            
        except Exception as e:
            self.logger.error(f"Error getting group worksheets: {e}")
            return False, f"Error getting group worksheets: {str(e)}", []
    
    async def upload_worksheet(
        self,
        groupId: str,
        title: str,
        file: UploadFile
    ) -> tuple[bool, str, Optional[str], Optional[str], Optional[str], Optional[str]]:
        """Upload a worksheet file."""
        self.logger.debug(f"upload_worksheet called with groupId={groupId}, title={title}")
        
        try:
            validated_data = await self._validate_worksheet_file(file)
            if not validated_data[0]:
                return (False, validated_data[1], None, None, None, None)
            
            file_type = validated_data[2]
            
            result = await self.groups_database.upload_worksheet_file(
                groupId=groupId,
                title=title,
                file=file,
                file_type=file_type
            )
            
            if result[0]:
                self.logger.info(f"Worksheet uploaded successfully: {result[2]}")
                return result
            else:
                return (False, result[1], None, None, None, None)
            
        except Exception as e:
            self.logger.error(f"Error uploading worksheet: {e}", exc_info=True)
            return (False, f"Error uploading worksheet: {str(e)}", None, None, None, None)
    
    async def _validate_worksheet_file(
        self,
        file: UploadFile
    ) -> tuple[bool, str, Optional[str]]:
        """Validate worksheet file type."""
        self.logger.debug(f"Validating file: {file.filename}")
        
        allowed_types = {
            'application/pdf': 'pdf',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'docx'
        }
        
        if file.content_type not in allowed_types:
            self.logger.warning(f"Invalid file type: {file.content_type}")
            return (False, "Only PDF and DOCX files are allowed", None)
        
        file_type = allowed_types[file.content_type]
        self.logger.debug(f"File validated successfully: {file_type}")
        return (True, "File validated", file_type)
    
    async def get_worksheet_file(self, file_id: str):
        """Get worksheet file from GridFS."""
        self.logger.debug(f"get_worksheet_file called with file_id={file_id}")
        try:
            return await self.groups_database.get_file_from_gridfs(file_id)
        except Exception as e:
            self.logger.error(f"Error getting worksheet file: {e}", exc_info=True)
            return None
    
    async def join_group(
        self,
        groupId: str,
        userId: str
    ) -> tuple[bool, str]:
        """Join a group."""
        try:
            group = await self.groups_database.get_group_by_id(groupId)
            if not group:
                return False, "Group not found"
            
            success = await self.groups_database.join_group(
                groupId=groupId,
                userId=userId
            )
            
            if success:
                self.logger.info(f"User {userId} joined group {groupId}")
                return True, "Successfully joined group"
            else:
                return False, "Failed to join group (may already be a member)"
                
        except Exception as e:
            self.logger.error(f"Error joining group: {e}")
            return False, f"Error joining group: {str(e)}"
    
    async def leave_group(
        self,
        groupId: str,
        userId: str
    ) -> tuple[bool, str]:
        """Leave a group."""
        try:
            group = await self.groups_database.get_group_by_id(groupId)
            if not group:
                return False, "Group not found"
            
            success = await self.groups_database.leave_group(
                groupId=groupId,
                userId=userId
            )
            
            if success:
                self.logger.info(f"User {userId} left group {groupId}")
                return True, "Successfully left group"
            else:
                return False, "Failed to leave group (may not be a member)"
                
        except Exception as e:
            self.logger.error(f"Error leaving group: {e}")
            return False, f"Error leaving group: {str(e)}"
    
    async def create_group_request(
        self,
        groupId: str,
        userId: str,
        requestMessage: str
    ) -> tuple[bool, str, Optional[str]]:
        """Create a new group request."""
        try:
            self.logger.debug(f"create_group_request called with groupId={groupId}, userId={userId}, requestMessage={requestMessage}")
            
            # Check if group exists
            group = await self.groups_database.get_group_by_id(groupId)
            if not group:
                self.logger.warning(f"Group {groupId} not found")
                return False, "Group not found", None
            
            # Check if user is already a member
            members = await self.groups_database.get_group_members(groupId)
            if any(str(member['userId']) == userId for member in members):
                self.logger.warning(f"User {userId} is already a member of group {groupId}")
                return False, "User is already a member of this group", None
            
            request_id = await self.groups_database.create_group_request(groupId, userId, requestMessage)
            
            if request_id:
                self.logger.info(f"Group request created successfully: {request_id}")
                return True, "Group request created successfully", request_id
            else:
                self.logger.warning(f"Failed to create group request (may already have pending request)")
                return False, "Failed to create group request (may already have pending request)", None
                
        except Exception as e:
            self.logger.error(f"Error creating group request: {e}", exc_info=True)
            return False, f"Error creating group request: {str(e)}", None
    
    async def get_group_requests(self, groupId: str) -> tuple[bool, str, List[dict]]:
        """Get all requests for a group."""
        try:
            self.logger.debug(f"get_group_requests called with groupId={groupId}")
            
            # Check if group exists
            group = await self.groups_database.get_group_by_id(groupId)
            if not group:
                self.logger.warning(f"Group {groupId} not found")
                return False, "Group not found", []
            
            requests = await self.groups_database.get_group_requests(groupId)
            
            self.logger.info(f"Retrieved {len(requests)} group request(s) for group {groupId}")
            return True, "Group requests retrieved successfully", requests
                
        except Exception as e:
            self.logger.error(f"Error getting group requests: {e}", exc_info=True)
            return False, f"Error getting group requests: {str(e)}", []
    
    async def create_group_role_config(
        self,
        groupId: str,
        roleName: str,
        permissions: List[str]
    ) -> tuple[bool, str, Optional[str]]:
        """Create a group-specific role configuration."""
        try:
            self.logger.debug(f"create_group_role_config called with groupId={groupId}, roleName={roleName}")
            
            group_role_id = await self.groups_database.create_group_role_config(
                groupId, roleName, permissions
            )
            
            if group_role_id:
                self.logger.info(f"Group role config created successfully: {group_role_id}")
                return True, "Group role config created successfully", group_role_id
            else:
                return False, "Failed to create group role config", None
                
        except Exception as e:
            self.logger.error(f"Error creating group role config: {e}", exc_info=True)
            return False, f"Error creating group role config: {str(e)}", None
    
    async def get_group_role_configs(self, groupId: str) -> tuple[bool, str, List[dict]]:
        """Get all role configurations for a group."""
        try:
            self.logger.debug(f"get_group_role_configs called with groupId={groupId}")
            
            group_roles = await self.groups_database.get_group_role_configs(groupId)
            
            self.logger.info(f"Retrieved {len(group_roles)} group role config(s)")
            return True, "Group role configs retrieved successfully", group_roles
                
        except Exception as e:
            self.logger.error(f"Error getting group role configs: {e}", exc_info=True)
            return False, f"Error getting group role configs: {str(e)}", []
    
    async def update_group_role_config(
        self,
        groupId: str,
        roleName: str,
        permissions: List[str]
    ) -> tuple[bool, str]:
        """Update a group role configuration."""
        try:
            self.logger.debug(f"update_group_role_config called with groupId={groupId}, roleName={roleName}")
            
            success = await self.groups_database.update_group_role_config(
                groupId, roleName, permissions
            )
            
            if success:
                self.logger.info(f"Group role config updated successfully")
                return True, "Group role config updated successfully"
            else:
                return False, "Failed to update group role config"
                
        except Exception as e:
            self.logger.error(f"Error updating group role config: {e}", exc_info=True)
            return False, f"Error updating group role config: {str(e)}"
    
    async def delete_group_role_config(
        self,
        groupId: str,
        roleName: str
    ) -> tuple[bool, str]:
        """Delete a group role configuration."""
        try:
            self.logger.debug(f"delete_group_role_config called with groupId={groupId}, roleName={roleName}")
            
            success = await self.groups_database.delete_group_role_config(groupId, roleName)
            
            if success:
                self.logger.info(f"Group role config deleted successfully")
                return True, "Group role config deleted successfully"
            else:
                return False, "Failed to delete group role config"
                
        except Exception as e:
            self.logger.error(f"Error deleting group role config: {e}", exc_info=True)
            return False, f"Error deleting group role config: {str(e)}"
    
    async def create_worksheet_text(
        self,
        groupId: str,
        title: str,
        content: str
    ) -> tuple[bool, str, str]:
        """Create a worksheet with HTML/text content."""
        self.logger.debug(f"create_worksheet_text called with groupId={groupId}, title={title}")
        
        try:
            # Validate inputs
            if not title or not title.strip():
                self.logger.warning("Title is empty")
                return False, "Title cannot be empty", ""
            
            if not content or not content.strip():
                self.logger.warning("Content is empty")
                return False, "Content cannot be empty", ""
            
            # Create worksheet entry in database
            worksheet_id = await self.groups_database.create_worksheet_text(
                groupId=groupId,
                title=title.strip(),
                content=content
            )
            
            if worksheet_id:
                self.logger.info(f"Worksheet created successfully: {worksheet_id}")
                return True, "Worksheet created successfully", worksheet_id
            else:
                self.logger.error("Failed to create worksheet entry")
                return False, "Failed to create worksheet entry", ""
                
        except Exception as e:
            self.logger.error(f"Error creating worksheet: {e}", exc_info=True)
            return False, f"Error creating worksheet: {str(e)}", ""

