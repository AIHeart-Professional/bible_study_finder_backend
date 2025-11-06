"""Users database - Data access layer."""
from typing import Optional
from datetime import datetime
from src.utils.logger import get_logger
from src.utils.config_loader import load_config
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from bson import ObjectId
import os

class UsersDatabase:
    """Database layer for user operations."""
    
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
        self.collection = self.db.users
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize the database and create indexes if they don't exist."""
        try:
            self.collection.create_index("email", unique=True)
            self.collection.create_index("username", unique=True)
            self.logger.info("Database initialized successfully")
        except Exception as e:
            self.logger.error(f"Error initializing database: {e}")
    
    async def create_user(
        self, 
        first_name: str, 
        last_name: str, 
        username: str, 
        email: str, 
        password_hash: str
    ) -> Optional[str]:
        """
        Create a new user in the database.
        
        Args:
            first_name: User's first name
            last_name: User's last name
            username: Unique username
            email: Unique email
            password_hash: Hashed password
            
        Returns:
            User ID if successful, None otherwise
        """
        try:
            user_doc = {
                'first_name': first_name,
                'last_name': last_name,
                'username': username,
                'email': email,
                'password_hash': password_hash,
                'created_date': datetime.utcnow(),
                'updated_date': datetime.utcnow()
            }
            result = self.collection.insert_one(user_doc)
            self.logger.info(f"User created successfully with ID: {result.inserted_id}")
            return str(result.inserted_id)
        except DuplicateKeyError as e:
            self.logger.error(f"User creation failed - duplicate key error: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Error creating user: {e}")
            return None
    
    async def get_user_by_email(self, email: str) -> Optional[dict]:
        """
        Get user by email.
        
        Args:
            email: User's email
            
        Returns:
            User dictionary if found, None otherwise
        """
        try:
            user = self.collection.find_one({'email': email})
            if user:
                user['id'] = str(user['_id'])
                del user['_id']
            return user
        except Exception as e:
            self.logger.error(f"Error fetching user by email: {e}")
            return None
    
    async def get_user_by_id(self, user_id: str) -> Optional[dict]:
        """
        Get user by ID.
        
        Args:
            user_id: User's ID (as string)
            
        Returns:
            User dictionary if found, None otherwise
        """
        try:
            user = self.collection.find_one({'_id': ObjectId(user_id)})
            if user:
                user['id'] = str(user['_id'])
                del user['_id']
            return user
        except Exception as e:
            self.logger.error(f"Error fetching user by ID: {e}")
            return None
    
    async def get_user_by_username(self, username: str) -> Optional[dict]:
        """
        Get user by username.
        
        Args:
            username: User's username
            
        Returns:
            User dictionary if found, None otherwise
        """
        try:
            user = self.collection.find_one({'username': username})
            if user:
                user['id'] = str(user['_id'])
                del user['_id']
            return user
        except Exception as e:
            self.logger.error(f"Error fetching user by username: {e}")
            return None
