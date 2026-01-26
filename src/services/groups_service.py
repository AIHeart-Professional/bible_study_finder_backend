"""Groups service - Application logic layer (BIGINT IDs)."""
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
    """Service for handling group business logic with BIGINT IDs."""
    
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
        leaderPublicId: str,
        location: dict,
        meetingStartTime: Optional[datetime] = None,
        meetingEndTime: Optional[datetime] = None,
        genderFocus: Optional[str] = None,
        meetingDays: Optional[List[str]] = None,
        demographic: Optional[str] = None,
        groupType: Optional[str] = None,
        meetingConsistency: Optional[str] = None,
        meetingFormat: Optional[str] = None,
        status: Optional[str] = None
    ) -> tuple[bool, str, Optional[str]]:
        """Create a new group."""
        try:
            location_dict = self._convert_location(location)
            group_public_id = await self.groups_database.create_group(
                name=name,
                description=description,
                leaderPublicId=leaderPublicId,
                location=location_dict,
                meetingStartTime=meetingStartTime,
                meetingEndTime=meetingEndTime,
                genderFocus=genderFocus,
                meetingDays=meetingDays,
                demographic=demographic,
                groupType=groupType,
                meetingConsistency=meetingConsistency,
                meetingFormat=meetingFormat,
                status=status
            )
            
            if group_public_id:
                self.logger.info(f"Group created successfully with public_id: {group_public_id}")
                return True, "Group created successfully", group_public_id
            else:
                return False, "Failed to create group (leader not found or invalid)", None
                
        except Exception as e:
            self.logger.error(f"Error creating group: {e}")
            return False, f"Error creating group: {str(e)}", None
    
    async def initialize_group(self, groupPublicId: str) -> tuple[bool, str]:
        """Initialize a group with empty arrays."""
        try:
            group = await self.groups_database.get_group_by_public_id(groupPublicId)
            if not group:
                return False, "Group not found"
            
            success = await self.groups_database.initialize_group(groupPublicId)
            if success:
                return True, "Group initialized successfully"
            else:
                return False, "Failed to initialize group"
                
        except Exception as e:
            self.logger.error(f"Error initializing group: {e}")
            return False, f"Error initializing group: {str(e)}"
    
    def _get_member_data(self, membership: dict) -> GroupMember:
        """Convert membership data to GroupMember model."""
        # membership already contains userId (public_id) and user details from JOIN
        return GroupMember(
            userId=str(membership.get('userId', '')),
            username=membership.get('username', ''),
            email=membership.get('email', ''),
            portraitUrl=membership.get('portraitUrl'),
            role=membership.get('role', 'member'),
            joinedAt=self._parse_datetime(membership.get('joinedAt'))
        )
    
    async def get_group_users(self, groupPublicId: str) -> tuple[bool, str, List[GroupMember], int]:
        """Get all users in a group."""
        try:
            group = await self.groups_database.get_group_by_public_id(groupPublicId)
            if not group:
                return False, "Group not found", [], 0
            
            memberships = await self.groups_database.get_group_members(groupPublicId)
            members = []
            
            for membership in memberships:
                # membership already contains user details from JOIN (username, email, portraitUrl)
                members.append(self._get_member_data(membership))
            
            member_count = len(members)
            return True, "Users retrieved successfully", members, member_count
            
        except Exception as e:
            self.logger.error(f"Error getting group users: {e}")
            return False, f"Error getting group users: {str(e)}", [], 0
    
    def _convert_chat_to_message(self, chat: dict) -> ChatMessage:
        """Convert chat data to ChatMessage model."""
        # chat already contains userId (public_id) and username from JOIN
        return ChatMessage(
            id=int(chat['id']),
            userId=str(chat.get('userId', '')),
            username=chat.get('username', ''),
            message=chat.get('message', ''),
            sentAt=self._parse_datetime(chat.get('sentAt'))
        )
    
    async def get_group_chat(self, groupPublicId: str) -> tuple[bool, str, List[ChatMessage]]:
        """Get all chat messages for a group."""
        try:
            group = await self.groups_database.get_group_by_public_id(groupPublicId)
            if not group:
                return False, "Group not found", []
            
            chats = await self.groups_database.get_group_chats(groupPublicId)
            messages = []
            
            for chat in chats:
                # chat already contains userId (public_id) and username from JOIN
                messages.append(self._convert_chat_to_message(chat))
            
            return True, "Chat messages retrieved successfully", messages
            
        except Exception as e:
            self.logger.error(f"Error getting group chat: {e}")
            return False, f"Error getting group chat: {str(e)}", []
    
    def _convert_meal_data_to_meal(self, meal_data: dict) -> Meal:
        """Convert meal data to Meal model."""
        return Meal(
            id=str(meal_data.get('id', '')),
            mealName=meal_data.get('mealName', ''),
            description=meal_data.get('description', ''),
            createdAt=self._parse_datetime(meal_data.get('createdAt'))
        )
    
    async def get_group_meals(self, groupPublicId: str) -> tuple[bool, str, List[Meal]]:
        """Get all meals for a group."""
        try:
            group = await self.groups_database.get_group_by_public_id(groupPublicId)
            if not group:
                return False, "Group not found", []
            
            meals_data = await self.groups_database.get_group_meals(groupPublicId)
            meals = [self._convert_meal_data_to_meal(meal_data) for meal_data in meals_data]
            
            return True, "Meals retrieved successfully", meals
            
        except Exception as e:
            self.logger.error(f"Error getting group meals: {e}")
            return False, f"Error getting group meals: {str(e)}", []
    
    def _convert_plan_data_to_plan(self, plan_data: dict) -> StudyPlan:
        """Convert plan data to StudyPlan model."""
        return StudyPlan(
            id=str(plan_data.get('id', '')),
            title=plan_data.get('title', ''),
            description=plan_data.get('description', ''),
            createdAt=self._parse_datetime(plan_data.get('createdAt'))
        )
    
    async def get_group_study_plans(self, groupPublicId: str) -> tuple[bool, str, List[StudyPlan]]:
        """Get all study plans for a group."""
        try:
            group = await self.groups_database.get_group_by_public_id(groupPublicId)
            if not group:
                return False, "Group not found", []
            
            study_plans_data = await self.groups_database.get_group_study_plans(groupPublicId)
            study_plans = [self._convert_plan_data_to_plan(plan_data) for plan_data in study_plans_data]
            
            return True, "Study plans retrieved successfully", study_plans
            
        except Exception as e:
            self.logger.error(f"Error getting group study plans: {e}")
            return False, f"Error getting group study plans: {str(e)}", []
    
    def _convert_group_data_to_group(self, group_data: dict) -> Group:
        """Convert group data to Group model."""
        location = Location(**group_data.get('location', {}))
        # leaderUserId is already a public_id string from database formatting
        return Group(
            public_id=str(group_data.get('public_id', '')),
            name=group_data.get('name', ''),
            description=group_data.get('description', ''),
            leaderUserId=str(group_data.get('leaderUserId', '')),
            leaderUsername=group_data.get('leaderUsername'),
            location=location,
            image=group_data.get('image'),
            meetingConsistency=group_data.get('meetingConsistency'),
            status=group_data.get('status'),
            meetingDays=group_data.get('meetingDays', []),
            meetingStartTime=self._parse_datetime(group_data.get('meetingStartTime')) if group_data.get('meetingStartTime') else None,
            meetingEndTime=self._parse_datetime(group_data.get('meetingEndTime')) if group_data.get('meetingEndTime') else None,
            genderFocus=group_data.get('genderFocus'),
            demographic=group_data.get('demographic'),
            groupType=group_data.get('groupType'),
            meetingFormat=group_data.get('meetingFormat'),
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
    
    async def get_group(self, groupPublicId: str) -> tuple[bool, str, Optional[Group]]:
        """Get a single group by public_id (UUID)."""
        try:
            group_data = await self.groups_database.get_group_by_public_id(groupPublicId)
            if not group_data:
                return False, "Group not found", None
            
            group = self._convert_group_data_to_group(group_data)
            return True, "Group retrieved successfully", group
        except Exception as e:
            self.logger.error(f"Error getting group: {e}")
            return False, f"Error getting group: {str(e)}", None
    
    async def get_groups_by_user_id(self, userPublicId: str) -> tuple[bool, str, List[Group]]:
        """Get all groups that a user is a member of."""
        try:
            groups_data = await self.groups_database.get_groups_by_user_id(userPublicId)
            groups = [self._convert_group_data_to_group(group_data) for group_data in groups_data]
            return True, "User groups retrieved successfully", groups
        except Exception as e:
            self.logger.error(f"Error getting groups by user ID: {e}")
            return False, f"Error getting user groups: {str(e)}", []
    
    async def create_group_chat(
        self,
        groupPublicId: str,
        userPublicId: str,
        message: str
    ) -> tuple[bool, str, Optional[int]]:
        """Create a new group chat message."""
        try:
            group = await self.groups_database.get_group_by_public_id(groupPublicId)
            if not group:
                return False, "Group not found", None
            
            chat_id = await self.groups_database.create_group_chat(
                groupPublicId=groupPublicId,
                userPublicId=userPublicId,
                message=message
            )
            
            if chat_id:
                self.logger.info(f"Group chat created successfully: {chat_id}")
                # Resolve IDs for notification
                group_id = await self.groups_database._resolve_group_id_from_public_id(groupPublicId)
                user_id = await self.groups_database._resolve_user_id_from_public_id(userPublicId)
                if group_id and user_id:
                    await self._send_chat_notifications(group_id, user_id, message, group)
                return True, "Group chat created successfully", chat_id
            else:
                return False, "Failed to create group chat", None
                
        except Exception as e:
            self.logger.error(f"Error creating group chat: {e}")
            return False, f"Error creating group chat: {str(e)}", None
    
    async def _send_chat_notifications(
        self,
        groupId: int,
        senderUserId: int,
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
                int(member['userId']) 
                for member in members 
                if int(member.get('userId')) != senderUserId
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
                group_id=str(groupId),
                group_name=group_name,
                sender_username=sender_username,
                message=message,
                recipient_user_ids=[str(rid) for rid in recipient_ids],
                fcm_tokens=fcm_tokens
            )
            
        except Exception as e:
            self.logger.error(f"Error sending chat notifications: {e}", exc_info=True)
    
    async def create_worksheet(
        self,
        groupPublicId: str,
        title: str,
        content: str
    ) -> tuple[bool, str, Optional[int]]:
        """Create a new Bible worksheet."""
        try:
            group = await self.groups_database.get_group_by_public_id(groupPublicId)
            if not group:
                return False, "Group not found", None
            
            worksheet_id = await self.groups_database.create_worksheet(
                groupPublicId=groupPublicId,
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
        # Get group public_id from worksheet data
        group_id = worksheet_data.get('group_id', 0)
        group_public_id = ""  # Will be resolved if needed
        if group_id:
            # Note: This would require a reverse lookup, but for now we'll use the group_id
            # In practice, worksheets should store public_id or we resolve it
            group_public_id = str(group_id)  # Temporary - should be resolved
        
        return Worksheet(
            id=int(worksheet_data['id']),
            groupPublicId=group_public_id,  # Should be resolved from group_id
            title=worksheet_data.get('title', ''),
            content=worksheet_data.get('content', ''),
            createdAt=self._parse_datetime(worksheet_data.get('createdAt')),
            updatedAt=self._parse_datetime(worksheet_data.get('updatedAt'))
        )
    
    async def get_group_worksheets(self, groupPublicId: str) -> tuple[bool, str, List[Worksheet]]:
        """Get all worksheets for a group."""
        try:
            group = await self.groups_database.get_group_by_public_id(groupPublicId)
            if not group:
                return False, "Group not found", []
            
            worksheets_data = await self.groups_database.get_group_worksheets(groupPublicId)
            # Update worksheets with group public_id
            for ws_data in worksheets_data:
                ws_data['groupPublicId'] = groupPublicId
            worksheets = [self._convert_worksheet_data_to_worksheet(ws_data) for ws_data in worksheets_data]
            
            return True, "Worksheets retrieved successfully", worksheets
            
        except Exception as e:
            self.logger.error(f"Error getting group worksheets: {e}")
            return False, f"Error getting group worksheets: {str(e)}", []
    
    async def upload_worksheet(
        self,
        groupPublicId: str,
        title: str,
        file: UploadFile
    ) -> tuple[bool, str, Optional[int], Optional[int], Optional[str], Optional[str]]:
        """Upload a worksheet file."""
        try:
            validated_data = await self._validate_worksheet_file(file)
            if not validated_data[0]:
                return (False, validated_data[1], None, None, None, None)
            
            file_type = validated_data[2]
            result = await self.groups_database.upload_worksheet_file(
                groupPublicId=groupPublicId,
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
    
    async def _validate_worksheet_file(self, file: UploadFile) -> tuple[bool, str, Optional[str]]:
        """Validate worksheet file type."""
        allowed_types = {
            'application/pdf': 'pdf',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'docx'
        }
        if file.content_type not in allowed_types:
            return (False, "Only PDF and DOCX files are allowed", None)
        return (True, "File validated", allowed_types[file.content_type])
    
    async def get_worksheet_file(self, file_id: int):
        """Get worksheet file from storage."""
        try:
            return await self.groups_database.get_file_from_postgres(file_id)
        except Exception as e:
            self.logger.error(f"Error getting worksheet file: {e}", exc_info=True)
            return None
    
    async def join_group(self, groupPublicId: str, userPublicId: str) -> tuple[bool, str]:
        """Join a group."""
        try:
            success = await self.groups_database.join_group(groupPublicId=groupPublicId, userPublicId=userPublicId)
            if success:
                return True, "Successfully joined group"
            else:
                return False, "Failed to join group (may already be a member)"
        except Exception as e:
            self.logger.error(f"Error joining group: {e}")
            return False, f"Error joining group: {str(e)}"
    
    async def leave_group(self, groupPublicId: str, userPublicId: str) -> tuple[bool, str]:
        """Leave a group."""
        try:
            success = await self.groups_database.leave_group(groupPublicId=groupPublicId, userPublicId=userPublicId)
            if success:
                return True, "Successfully left group"
            else:
                return False, "Failed to leave group (may not be a member)"
        except Exception as e:
            self.logger.error(f"Error leaving group: {e}")
            return False, f"Error leaving group: {str(e)}"
    
    async def create_group_request(self, groupPublicId: str, userPublicId: str, requestMessage: str) -> tuple[bool, str, Optional[int]]:
        """Create a new group request."""
        try:
            request_id = await self.groups_database.create_group_request(groupPublicId, userPublicId, requestMessage)
            if request_id:
                return True, "Group request created successfully", request_id
            return False, "Failed to create group request", None
        except Exception as e:
            self.logger.error(f"Error creating group request: {e}", exc_info=True)
            return False, f"Error creating group request: {str(e)}", None
    
    async def get_group_requests(self, groupPublicId: str) -> tuple[bool, str, List[dict]]:
        """Get all requests for a group."""
        try:
            requests = await self.groups_database.get_group_requests(groupPublicId)
            return True, "Group requests retrieved successfully", requests
        except Exception as e:
            self.logger.error(f"Error getting group requests: {e}", exc_info=True)
            return False, f"Error getting group requests: {str(e)}", []
    
    async def create_group_role_config(self, groupPublicId: str, roleName: str, permissions: List[str]) -> tuple[bool, str, Optional[int]]:
        """Create a group-specific role configuration."""
        try:
            group_role_id = await self.groups_database.create_group_role_config(groupPublicId, roleName, permissions)
            if group_role_id:
                return True, "Group role config created successfully", group_role_id
            return False, "Failed to create group role config", None
        except Exception as e:
            self.logger.error(f"Error creating group role config: {e}", exc_info=True)
            return False, f"Error creating group role config: {str(e)}", None
    
    async def get_group_role_configs(self, groupPublicId: str) -> tuple[bool, str, List[dict]]:
        """Get all role configurations for a group."""
        try:
            group_roles = await self.groups_database.get_group_role_configs(groupPublicId)
            return True, "Group role configs retrieved successfully", group_roles
        except Exception as e:
            self.logger.error(f"Error getting group role configs: {e}", exc_info=True)
            return False, f"Error getting group role configs: {str(e)}", []
    
    async def update_group_role_config(self, groupPublicId: str, roleName: str, permissions: List[str]) -> tuple[bool, str]:
        """Update a group role configuration."""
        try:
            success = await self.groups_database.update_group_role_config(groupPublicId, roleName, permissions)
            if success:
                return True, "Group role config updated successfully"
            return False, "Failed to update group role config"
        except Exception as e:
            self.logger.error(f"Error updating group role config: {e}", exc_info=True)
            return False, f"Error updating group role config: {str(e)}"
    
    async def delete_group_role_config(self, groupPublicId: str, roleName: str) -> tuple[bool, str]:
        """Delete a group role configuration."""
        try:
            success = await self.groups_database.delete_group_role_config(groupPublicId, roleName)
            if success:
                return True, "Group role config deleted successfully"
            return False, "Failed to delete group role config"
        except Exception as e:
            self.logger.error(f"Error deleting group role config: {e}", exc_info=True)
            return False, f"Error deleting group role config: {str(e)}"
    
    async def create_worksheet_text(self, groupPublicId: str, title: str, content: str) -> tuple[bool, str, str]:
        """Create a worksheet with HTML/text content."""
        try:
            worksheet_id = await self.groups_database.create_worksheet_text(groupPublicId=groupPublicId, title=title.strip(), content=content)
            if worksheet_id:
                return True, "Worksheet created successfully", worksheet_id
            return False, "Failed to create worksheet entry", ""
        except Exception as e:
            self.logger.error(f"Error creating worksheet: {e}", exc_info=True)
            return False, f"Error creating worksheet: {str(e)}", ""
