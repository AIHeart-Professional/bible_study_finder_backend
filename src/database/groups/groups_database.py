"""Groups database - Data access layer."""
from typing import Optional, List
from datetime import datetime
from src.utils.logger import get_logger
from src.utils.config_loader import load_config
from pymongo import MongoClient
from bson import ObjectId
import os

class GroupsDatabase:
    """Database layer for group operations."""
    
    def __init__(self):
        """Initialize the database connection."""
        self.logger = get_logger(__name__)
        self.config = load_config()
        config_url = self.config.get('database', {}).get('url', 'mongodb://localhost:27017')
        self.db_url = os.getenv("DATABASE_URL") or config_url
        if self.db_url and self.db_url.startswith("${"):
            self.db_url = 'mongodb://localhost:27017'
        self.db_name = self.config.get('database', {}).get('name', 'bible_study_finder')
        self.client = MongoClient(self.db_url)
        self.db = self.client[self.db_name]
        self.groups_collection = self.db.groups
        self.memberships_collection = self.db.groupmemberships
        self.chats_collection = self.db.groupchats
        self.worksheets_collection = self.db.bibleworksheets
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize the database and create indexes if they don't exist."""
        try:
            self.groups_collection.create_index("leaderUserId")
            self.memberships_collection.create_index([("groupId", 1), ("userId", 1)], unique=True)
            self.memberships_collection.create_index("groupId")
            self.memberships_collection.create_index("userId")
            self.chats_collection.create_index("groupId")
            self.worksheets_collection.create_index("groupId")
            self.logger.info("Groups database initialized successfully")
        except Exception as e:
            self.logger.error(f"Error initializing groups database: {e}")
    
    async def create_group(
        self,
        name: str,
        description: str,
        leaderUserId: str,
        location: dict
    ) -> Optional[str]:
        """Create a new group in the database."""
        try:
            group_doc = {
                'name': name,
                'description': description,
                'leaderUserId': ObjectId(leaderUserId),
                'location': location,
                'studyPlans': [],
                'meals': [],
                'createdAt': datetime.utcnow(),
                'updatedAt': datetime.utcnow()
            }
            result = self.groups_collection.insert_one(group_doc)
            self.logger.info(f"Group created successfully with ID: {result.inserted_id}")
            return str(result.inserted_id)
        except Exception as e:
            self.logger.error(f"Error creating group: {e}")
            return None
    
    async def initialize_group(self, groupId: str) -> bool:
        """Initialize a group with empty arrays."""
        try:
            result = self.groups_collection.update_one(
                {'_id': ObjectId(groupId)},
                {
                    '$set': {
                        'studyPlans': [],
                        'meals': [],
                        'updatedAt': datetime.utcnow()
                    }
                }
            )
            return result.modified_count > 0
        except Exception as e:
            self.logger.error(f"Error initializing group: {e}")
            return False
    
    async def get_all_groups(self) -> List[dict]:
        """Get all groups from the database."""
        try:
            groups = self.groups_collection.find()
            group_list = []
            for group in groups:
                group['id'] = str(group['_id'])
                del group['_id']
                if 'leaderUserId' in group:
                    group['leaderUserId'] = str(group['leaderUserId'])
                group_list.append(group)
            return group_list
        except Exception as e:
            self.logger.error(f"Error fetching all groups: {e}")
            return []
    
    async def get_group_by_id(self, groupId: str) -> Optional[dict]:
        """Get group by ID."""
        try:
            group = self.groups_collection.find_one({'_id': ObjectId(groupId)})
            if group:
                group['id'] = str(group['_id'])
                del group['_id']
                if 'leaderUserId' in group:
                    group['leaderUserId'] = str(group['leaderUserId'])
            return group
        except Exception as e:
            self.logger.error(f"Error fetching group by ID: {e}")
            return None
    
    async def get_group_members(self, groupId: str) -> List[dict]:
        """Get all members of a group."""
        try:
            memberships = self.memberships_collection.find({'groupId': ObjectId(groupId)})
            members = []
            for membership in memberships:
                membership['id'] = str(membership['_id'])
                del membership['_id']
                membership['groupId'] = str(membership['groupId'])
                membership['userId'] = str(membership['userId'])
                members.append(membership)
            return members
        except Exception as e:
            self.logger.error(f"Error fetching group members: {e}")
            return []
    
    async def get_group_chats(self, groupId: str) -> List[dict]:
        """Get all chat messages for a group."""
        try:
            chats = self.chats_collection.find({'groupId': ObjectId(groupId)}).sort('sentAt', 1)
            chat_list = []
            for chat in chats:
                chat['id'] = str(chat['_id'])
                del chat['_id']
                chat['groupId'] = str(chat['groupId'])
                chat['userId'] = str(chat['userId'])
                chat_list.append(chat)
            return chat_list
        except Exception as e:
            self.logger.error(f"Error fetching group chats: {e}")
            return []
    
    async def get_group_meals(self, groupId: str) -> List[dict]:
        """Get all meals for a group."""
        try:
            group = await self.get_group_by_id(groupId)
            if group and 'meals' in group:
                meals = []
                for meal in group['meals']:
                    if '_id' in meal:
                        meal['id'] = str(meal['_id'])
                        del meal['_id']
                    meals.append(meal)
                return meals
            return []
        except Exception as e:
            self.logger.error(f"Error fetching group meals: {e}")
            return []
    
    async def get_group_study_plans(self, groupId: str) -> List[dict]:
        """Get all study plans for a group."""
        try:
            group = await self.get_group_by_id(groupId)
            if group and 'studyPlans' in group:
                plans = []
                for plan in group['studyPlans']:
                    if '_id' in plan:
                        plan['id'] = str(plan['_id'])
                        del plan['_id']
                    plans.append(plan)
                return plans
            return []
        except Exception as e:
            self.logger.error(f"Error fetching group study plans: {e}")
            return []
    
    async def get_user_by_id(self, userId: str) -> Optional[dict]:
        """Get user by ID from users collection."""
        try:
            users_collection = self.db.users
            user = users_collection.find_one({'_id': ObjectId(userId)})
            if user:
                user['id'] = str(user['_id'])
                del user['_id']
            return user
        except Exception as e:
            self.logger.error(f"Error fetching user by ID: {e}")
            return None
    
    async def create_group_chat(
        self,
        groupId: str,
        userId: str,
        message: str
    ) -> Optional[str]:
        """Create a new group chat message."""
        try:
            chat_doc = {
                'groupId': ObjectId(groupId),
                'userId': ObjectId(userId),
                'message': message,
                'sentAt': datetime.utcnow()
            }
            result = self.chats_collection.insert_one(chat_doc)
            self.logger.info(f"Group chat created successfully with ID: {result.inserted_id}")
            return str(result.inserted_id)
        except Exception as e:
            self.logger.error(f"Error creating group chat: {e}")
            return None
    
    async def create_worksheet(
        self,
        groupId: str,
        title: str,
        content: str
    ) -> Optional[str]:
        """Create a new Bible worksheet."""
        try:
            worksheet_doc = {
                'groupId': ObjectId(groupId),
                'title': title,
                'content': content,
                'createdAt': datetime.utcnow(),
                'updatedAt': datetime.utcnow()
            }
            result = self.worksheets_collection.insert_one(worksheet_doc)
            self.logger.info(f"Worksheet created successfully with ID: {result.inserted_id}")
            return str(result.inserted_id)
        except Exception as e:
            self.logger.error(f"Error creating worksheet: {e}")
            return None
    
    async def get_group_worksheets(self, groupId: str) -> List[dict]:
        """Get all worksheets for a group."""
        try:
            worksheets = self.worksheets_collection.find({'groupId': ObjectId(groupId)}).sort('createdAt', -1)
            worksheet_list = []
            for worksheet in worksheets:
                worksheet['id'] = str(worksheet['_id'])
                del worksheet['_id']
                worksheet['groupId'] = str(worksheet['groupId'])
                worksheet_list.append(worksheet)
            return worksheet_list
        except Exception as e:
            self.logger.error(f"Error fetching group worksheets: {e}")
            return []

