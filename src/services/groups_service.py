"""Groups service - Application logic layer."""
from typing import List, Optional
from datetime import datetime
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

class GroupsService:
    """Service for handling group business logic."""
    
    def __init__(self):
        """Initialize the service and database."""
        self.logger = get_logger(__name__)
        self.groups_database = GroupsDatabase()
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
    
    def _convert_membership_to_member(self, membership: dict, user: dict) -> GroupMember:
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
                    members.append(self._convert_membership_to_member(membership, user))
            
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
                return True, "Group chat created successfully", chat_id
            else:
                return False, "Failed to create group chat", None
                
        except Exception as e:
            self.logger.error(f"Error creating group chat: {e}")
            return False, f"Error creating group chat: {str(e)}", None
    
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

