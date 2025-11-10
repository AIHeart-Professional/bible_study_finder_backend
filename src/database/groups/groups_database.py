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
        self.roles_collection = self.db.roles
        self.permissions_collection = self.db.permissions
        self.group_roles_collection = self.db.grouproles
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
            self.roles_collection.create_index("name", unique=True)
            self.permissions_collection.create_index("action", unique=True)
            self.group_roles_collection.create_index([("groupId", 1), ("userId", 1)], unique=True)
            self.group_roles_collection.create_index("groupId")
            self.group_roles_collection.create_index("userId")
            self.logger.info("Groups database initialized successfully")
        except Exception as e:
            self.logger.error(f"Error initializing groups database: {e}")
    
    async def create_group(
        self,
        name: str,
        description: str,
        leaderUserId: str,
        location: dict,
        image: Optional[str] = None
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
            if image:
                group_doc['image'] = image
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
    
    async def join_group(
        self,
        groupId: str,
        userId: str
    ) -> bool:
        """Join a group by creating a membership record."""
        try:
            existing = self.memberships_collection.find_one({
                'groupId': ObjectId(groupId),
                'userId': ObjectId(userId)
            })
            
            if existing:
                self.logger.warning(f"User {userId} is already a member of group {groupId}")
                return False
            
            membership_doc = {
                'groupId': ObjectId(groupId),
                'userId': ObjectId(userId),
                'role': 'member',
                'joinedAt': datetime.utcnow()
            }
            result = self.memberships_collection.insert_one(membership_doc)
            self.logger.info(f"User {userId} joined group {groupId} with membership ID: {result.inserted_id}")
            return True
        except Exception as e:
            self.logger.error(f"Error joining group: {e}")
            return False
    
    async def leave_group(
        self,
        groupId: str,
        userId: str
    ) -> bool:
        """Leave a group by removing the membership record."""
        try:
            result = self.memberships_collection.delete_one({
                'groupId': ObjectId(groupId),
                'userId': ObjectId(userId)
            })
            
            if result.deleted_count > 0:
                self.logger.info(f"User {userId} left group {groupId}")
                return True
            else:
                self.logger.warning(f"User {userId} is not a member of group {groupId}")
                return False
        except Exception as e:
            self.logger.error(f"Error leaving group: {e}")
            return False
    
    async def get_groups_by_user_id(self, userId: str) -> List[dict]:
        """Get all groups that a user is a member of."""
        try:
            # Find all memberships for this user
            memberships = self.memberships_collection.find({'userId': ObjectId(userId)})
            group_ids = [membership['groupId'] for membership in memberships]
            
            if not group_ids:
                return []
            
            # Get all groups for these group IDs
            groups = self.groups_collection.find({'_id': {'$in': group_ids}})
            group_list = []
            for group in groups:
                group['id'] = str(group['_id'])
                del group['_id']
                if 'leaderUserId' in group:
                    group['leaderUserId'] = str(group['leaderUserId'])
                group_list.append(group)
            
            return group_list
        except Exception as e:
            self.logger.error(f"Error fetching groups by user ID: {e}")
            return []
    
    # Role Management Methods
    async def create_permission(self, action: str, description: str) -> Optional[str]:
        """Create a new permission."""
        try:
            permission_doc = {
                'action': action,
                'description': description
            }
            result = self.permissions_collection.insert_one(permission_doc)
            self.logger.info(f"Permission created successfully with ID: {result.inserted_id}")
            return str(result.inserted_id)
        except Exception as e:
            self.logger.error(f"Error creating permission: {e}")
            return None
    
    async def get_all_permissions(self) -> List[dict]:
        """Get all permissions."""
        try:
            permissions = self.permissions_collection.find()
            permission_list = []
            for permission in permissions:
                permission['id'] = str(permission['_id'])
                del permission['_id']
                permission_list.append(permission)
            return permission_list
        except Exception as e:
            self.logger.error(f"Error fetching permissions: {e}")
            return []
    
    async def get_permission_by_id(self, permissionId: str) -> Optional[dict]:
        """Get a permission by ID."""
        try:
            permission = self.permissions_collection.find_one({'_id': ObjectId(permissionId)})
            if permission:
                permission['id'] = str(permission['_id'])
                del permission['_id']
            return permission
        except Exception as e:
            self.logger.error(f"Error fetching permission by ID: {e}")
            return None
    
    async def update_permission(
        self,
        permissionId: str,
        action: Optional[str] = None,
        description: Optional[str] = None
    ) -> bool:
        """Update a permission."""
        try:
            update_data = {}
            if action is not None:
                update_data['action'] = action
            if description is not None:
                update_data['description'] = description
            
            if not update_data:
                return False
            
            result = self.permissions_collection.update_one(
                {'_id': ObjectId(permissionId)},
                {'$set': update_data}
            )
            
            if result.modified_count > 0:
                self.logger.info(f"Updated permission {permissionId}")
                return True
            else:
                self.logger.warning(f"Permission {permissionId} not found or no changes")
                return False
        except Exception as e:
            self.logger.error(f"Error updating permission: {e}")
            return False
    
    async def create_role(self, name: str, permissions: List[str]) -> Optional[str]:
        """Create a new role."""
        try:
            role_doc = {
                'name': name,
                'permissions': permissions
            }
            result = self.roles_collection.insert_one(role_doc)
            self.logger.info(f"Role created successfully with ID: {result.inserted_id}")
            return str(result.inserted_id)
        except Exception as e:
            self.logger.error(f"Error creating role: {e}")
            return None
    
    async def get_all_roles(self) -> List[dict]:
        """Get all roles."""
        try:
            roles = self.roles_collection.find()
            role_list = []
            for role in roles:
                role['id'] = str(role['_id'])
                del role['_id']
                role_list.append(role)
            return role_list
        except Exception as e:
            self.logger.error(f"Error fetching roles: {e}")
            return []
    
    async def get_role_by_id(self, roleId: str) -> Optional[dict]:
        """Get a role by ID."""
        try:
            role = self.roles_collection.find_one({'_id': ObjectId(roleId)})
            if role:
                role['id'] = str(role['_id'])
                del role['_id']
            return role
        except Exception as e:
            self.logger.error(f"Error fetching role by ID: {e}")
            return None
    
    async def update_role(
        self,
        roleId: str,
        name: Optional[str] = None,
        permissions: Optional[List[str]] = None
    ) -> bool:
        """Update a role."""
        try:
            update_data = {}
            if name is not None:
                update_data['name'] = name
            if permissions is not None:
                update_data['permissions'] = permissions
            
            if not update_data:
                return False
            
            result = self.roles_collection.update_one(
                {'_id': ObjectId(roleId)},
                {'$set': update_data}
            )
            
            if result.modified_count > 0:
                self.logger.info(f"Updated role {roleId}")
                return True
            else:
                self.logger.warning(f"Role {roleId} not found or no changes")
                return False
        except Exception as e:
            self.logger.error(f"Error updating role: {e}")
            return False
    
    async def get_role_by_name(self, name: str) -> Optional[dict]:
        """Get a role by name."""
        try:
            role = self.roles_collection.find_one({'name': name})
            if role:
                role['id'] = str(role['_id'])
                del role['_id']
            return role
        except Exception as e:
            self.logger.error(f"Error fetching role by name: {e}")
            return None
    
    async def create_group_role(
        self,
        userId: str,
        groupId: str,
        role: str
    ) -> Optional[str]:
        """Assign a role to a user in a group."""
        try:
            # Check if role exists
            role_doc = await self.get_role_by_name(role)
            if not role_doc:
                self.logger.error(f"Role '{role}' does not exist")
                return None
            
            # Check if group role already exists
            existing = self.group_roles_collection.find_one({
                'groupId': ObjectId(groupId),
                'userId': ObjectId(userId)
            })
            
            if existing:
                # Check if role name matches - extract role from existing document
                existing_role = existing.get('role')
                if existing_role and existing_role == role:
                    self.logger.info(f"Group role already exists with same role '{role}' for user {userId} in group {groupId}")
                    return str(existing['_id'])
                
                # Role name doesn't match or doesn't exist, update it
                result = self.group_roles_collection.update_one(
                    {
                        'groupId': ObjectId(groupId),
                        'userId': ObjectId(userId)
                    },
                    {
                        '$set': {'role': role}
                    }
                )
                if result.modified_count > 0:
                    old_role = existing_role if existing_role else 'none'
                    self.logger.info(f"Updated group role for user {userId} in group {groupId} from '{old_role}' to '{role}'")
                    return str(existing['_id'])
                elif result.matched_count > 0:
                    # Document matched but wasn't modified (same role)
                    self.logger.info(f"Group role already set to '{role}' for user {userId} in group {groupId}")
                    return str(existing['_id'])
                return None
            else:
                # Create new group role
                group_role_doc = {
                    'userId': ObjectId(userId),
                    'groupId': ObjectId(groupId),
                    'role': role
                }
                result = self.group_roles_collection.insert_one(group_role_doc)
                self.logger.info(f"Group role created successfully with ID: {result.inserted_id}")
                return str(result.inserted_id)
        except Exception as e:
            self.logger.error(f"Error creating group role: {e}")
            return None
    
    async def update_group_role(
        self,
        userId: str,
        groupId: str,
        role: str
    ) -> bool:
        """Update a group role."""
        try:
            # Check if role exists
            role_doc = await self.get_role_by_name(role)
            if not role_doc:
                self.logger.error(f"Role '{role}' does not exist")
                return False
            
            result = self.group_roles_collection.update_one(
                {
                    'groupId': ObjectId(groupId),
                    'userId': ObjectId(userId)
                },
                {
                    '$set': {'role': role}
                }
            )
            
            if result.modified_count > 0:
                self.logger.info(f"Updated group role for user {userId} in group {groupId} to {role}")
                return True
            else:
                self.logger.warning(f"Group role not found for user {userId} in group {groupId}")
                return False
        except Exception as e:
            self.logger.error(f"Error updating group role: {e}")
            return False
    
    async def get_group_roles(self, groupId: Optional[str] = None, userId: Optional[str] = None) -> List[dict]:
        """Get group roles, optionally filtered by groupId or userId."""
        try:
            query = {}
            if groupId:
                query['groupId'] = ObjectId(groupId)
            if userId:
                query['userId'] = ObjectId(userId)
            
            group_roles = self.group_roles_collection.find(query)
            role_list = []
            for group_role in group_roles:
                group_role['id'] = str(group_role['_id'])
                del group_role['_id']
                group_role['userId'] = str(group_role['userId'])
                group_role['groupId'] = str(group_role['groupId'])
                role_list.append(group_role)
            return role_list
        except Exception as e:
            self.logger.error(f"Error fetching group roles: {e}")
            return []
    
    async def remove_group_role(self, userId: str, groupId: str) -> bool:
        """Remove a role from a user in a group."""
        try:
            result = self.group_roles_collection.delete_one({
                'groupId': ObjectId(groupId),
                'userId': ObjectId(userId)
            })
            
            if result.deleted_count > 0:
                self.logger.info(f"Removed group role for user {userId} in group {groupId}")
                return True
            else:
                self.logger.warning(f"Group role not found for user {userId} in group {groupId}")
                return False
        except Exception as e:
            self.logger.error(f"Error removing group role: {e}")
            return False
    
    async def get_user_role_in_group(self, groupId: str, userId: str) -> Optional[str]:
        """Get a user's role in a specific group from groupRoles collection."""
        try:
            group_role = self.group_roles_collection.find_one({
                'groupId': ObjectId(groupId),
                'userId': ObjectId(userId)
            })
            
            if group_role:
                return group_role.get('role')
            
            # Check if user is the group leader
            group = await self.get_group_by_id(groupId)
            if group and str(group.get('leaderUserId')) == userId:
                return 'leader'
            
            return None
        except Exception as e:
            self.logger.error(f"Error getting user role in group: {e}")
            return None
    
    async def remove_permission(self, permissionId: str) -> bool:
        """Remove a permission."""
        try:
            result = self.permissions_collection.delete_one({'_id': ObjectId(permissionId)})
            
            if result.deleted_count > 0:
                self.logger.info(f"Removed permission {permissionId}")
                return True
            else:
                self.logger.warning(f"Permission {permissionId} not found")
                return False
        except Exception as e:
            self.logger.error(f"Error removing permission: {e}")
            return False
    
    async def remove_role(self, roleId: str) -> bool:
        """Remove a role."""
        try:
            result = self.roles_collection.delete_one({'_id': ObjectId(roleId)})
            
            if result.deleted_count > 0:
                self.logger.info(f"Removed role {roleId}")
                return True
            else:
                self.logger.warning(f"Role {roleId} not found")
                return False
        except Exception as e:
            self.logger.error(f"Error removing role: {e}")
            return False
    
    async def remove_role_from_group(self, groupId: str, role: str) -> int:
        """Remove all group roles matching a specific role name from a group."""
        try:
            result = self.group_roles_collection.delete_many({
                'groupId': ObjectId(groupId),
                'role': role
            })
            
            if result.deleted_count > 0:
                self.logger.info(f"Removed {result.deleted_count} group role(s) with role '{role}' from group {groupId}")
            else:
                self.logger.warning(f"No group roles found with role '{role}' in group {groupId}")
            
            return result.deleted_count
        except Exception as e:
            self.logger.error(f"Error removing role from group: {e}")
            return 0

