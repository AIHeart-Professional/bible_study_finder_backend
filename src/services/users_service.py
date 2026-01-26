"""Users service - Application logic layer."""
from typing import Optional
from datetime import datetime
from src.models.users import User
from src.utils.logger import get_logger
from src.database.users.users_database import UsersDatabase
import bcrypt
import jwt
import os

class UsersService:
    """Service for handling user business logic."""
    
    def __init__(self):
        """Initialize the service and database."""
        self.logger = get_logger(__name__)
        self.users_database = UsersDatabase()
        self.secret_key = os.getenv("JWT_SECRET", "your-secret-key-here-change-in-production")
        self.logger.info("UsersService initialized successfully")
    
    def _hash_password(self, password: str) -> str:
        """
        Hash a password using bcrypt.
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password
        """
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def _verify_password(self, password: str, password_hash: str) -> bool:
        """
        Verify a password against a hash.
        
        Args:
            password: Plain text password
            password_hash: Hashed password
            
        Returns:
            True if password matches, False otherwise
        """
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    
    def _generate_token(self, user_id: int, email: str) -> str:
        """
        Generate a JWT token for the user.
        
        Args:
            user_id: User's ID (int)
            email: User's email
            
        Returns:
            JWT token string
        """
        payload = {
            'user_id': user_id,
            'email': email,
            'exp': datetime.utcnow().timestamp() + 86400  # 24 hours
        }
        return jwt.encode(payload, self.secret_key, algorithm='HS256')
    
    def _parse_datetime(self, dt_value) -> datetime:
        """
        Parse datetime value to datetime object.
        
        Args:
            dt_value: Datetime value (datetime, str, or None)
            
        Returns:
            datetime object
        """
        if isinstance(dt_value, datetime):
            return dt_value
        if isinstance(dt_value, str):
            return datetime.fromisoformat(dt_value.replace('Z', '+00:00').split('.')[0])
        return datetime.utcnow()
    
    def _convert_to_user_model(self, user_data: dict) -> User:
        """
        Convert database user dict to User model.
        
        Args:
            user_data: User dictionary from database
            
        Returns:
            User model instance
        """
        return User(
            public_id=str(user_data.get('public_id', '')),
            first_name=user_data['first_name'],
            last_name=user_data['last_name'],
            username=user_data['username'],
            email=user_data['email'],
            created_date=self._parse_datetime(user_data.get('created_date')),
            updated_date=self._parse_datetime(user_data.get('updated_date'))
        )
    
    async def create_user(
        self,
        first_name: str,
        last_name: str,
        username: str,
        email: str,
        password: str
    ) -> tuple[bool, str]:
        """
        Create a new user.
        
        Args:
            first_name: User's first name
            last_name: User's last name
            username: Unique username
            email: Unique email
            password: Plain text password
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            existing_user = await self.users_database.get_user_by_email(email)
            if existing_user:
                return False, "User with this email already exists"
            
            existing_username = await self.users_database.get_user_by_username(username)
            if existing_username:
                return False, "User with this username already exists"
            
            password_hash = self._hash_password(password)
            user_id = await self.users_database.create_user(
                first_name=first_name,
                last_name=last_name,
                username=username,
                email=email,
                password_hash=password_hash
            )
            
            if user_id:
                self.logger.info(f"User created successfully: {user_id}")
                return True, "User created successfully"
            else:
                return False, "Failed to create user"
                
        except Exception as e:
            self.logger.error(f"Error creating user: {e}")
            return False, f"Error creating user: {str(e)}"
    
    async def login_user(self, email: str, password: str) -> tuple[bool, str, Optional[User], Optional[str]]:
        """
        Authenticate a user.
        
        Args:
            email: User's email
            password: Plain text password
            
        Returns:
            Tuple of (authenticated: bool, message: str, user: Optional[User], token: Optional[str])
        """
        try:
            user_data = await self.users_database.get_user_by_email(email)
            
            if not user_data:
                return False, "Invalid email or password", None, None
            
            if not self._verify_password(password, user_data['password_hash']):
                return False, "Invalid email or password", None, None
            
            token = self._generate_token(str(user_data['id']), user_data['email'])
            user = self._convert_to_user_model(user_data)
            
            self.logger.info(f"User logged in successfully: {user.email}")
            return True, "Login successful", user, token
            
        except Exception as e:
            self.logger.error(f"Error during login: {e}")
            return False, f"Error during login: {str(e)}", None, None
    
    async def get_user(self, email: str) -> tuple[bool, str, Optional[User]]:
        """
        Get user information by email.
        
        Args:
            email: User's email
            
        Returns:
            Tuple of (success: bool, message: str, user: Optional[User])
        """
        try:
            user_data = await self.users_database.get_user_by_email(email)
            if not user_data:
                return False, "User not found", None
            
            user = self._convert_to_user_model(user_data)
            return True, "User found", user
            
        except Exception as e:
            self.logger.error(f"Error getting user: {e}")
            return False, f"Error getting user: {str(e)}", None
    
    async def register_fcm_token(self, user_id: int, fcm_token: str) -> tuple[bool, str]:
        """
        Register FCM token for a user.
        
        Args:
            user_id: User's ID (int)
            fcm_token: FCM token string
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            self.logger.debug(f"Registering FCM token for user: {user_id}")
            success = await self.users_database.register_fcm_token(user_id, fcm_token)
            if success:
                self.logger.info(f"FCM token registered successfully for user: {user_id}")
                return True, "FCM token registered successfully"
            else:
                return False, "Failed to register FCM token"
        except Exception as e:
            self.logger.error(f"Error registering FCM token: {e}")
            return False, f"Error registering FCM token: {str(e)}"

    async def unregister_fcm_token(self, user_id: int) -> tuple[bool, str]:
        """
        Unregister FCM token for a user.
        
        Args:
            user_id: User's ID (int)
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            self.logger.debug(f"Unregistering FCM token for user: {user_id}")
            success = await self.users_database.unregister_fcm_token(user_id)
            if success:
                self.logger.info(f"FCM token unregistered successfully for user: {user_id}")
                return True, "FCM token unregistered successfully"
            else:
                return False, "Failed to unregister FCM token"
        except Exception as e:
            self.logger.error(f"Error unregistering FCM token: {e}")
            return False, f"Error unregistering FCM token: {str(e)}"