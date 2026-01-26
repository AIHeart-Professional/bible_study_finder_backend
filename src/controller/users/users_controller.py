"""Users controller - Business logic distributor layer."""
from typing import Optional, List
from src.models.users import (
    create_user_response,
    login_user_response,
    get_user_response,
    register_fcm_token_request,
    register_fcm_token_response,
    unregister_fcm_token_request,
    unregister_fcm_token_response,
    User
)
from src.utils.logger import get_logger
from src.services.users_service import UsersService

class UsersController:
    """Controller for handling user business logic."""
    
    def __init__(self):
        """Initialize the controller and user service."""
        self.users_service = UsersService()
        self.logger = get_logger(__name__)
    
    async def create_user(
        self,
        first_name: str,
        last_name: str,
        username: str,
        email: str,
        password: str,
        attended_churches: Optional[List[int]] = None
    ) -> create_user_response:
        """
        Create a new user.
        
        Args:
            first_name: User's first name
            last_name: User's last name
            username: Unique username
            email: Unique email
            password: Plain text password
            
        Returns:
            create_user_response object
        """
        try:
            success, message = await self.users_service.create_user(
                first_name=first_name,
                last_name=last_name,
                username=username,
                email=email,
                password=password
            )
            
            return create_user_response(
                created=success,
                message=message
            )
        except Exception as e:
            self.logger.error(f"Error in create_user controller: {e}")
            return create_user_response(
                created=False,
                message=f"Error creating user: {str(e)}"
            )
    
    async def login_user(self, email: str, password: str) -> login_user_response:
        """
        Authenticate a user.
        
        Args:
            email: User's email
            password: Plain text password
            
        Returns:
            login_user_response object
        """
        try:
            authenticated, message, user, token = await self.users_service.login_user(
                email=email,
                password=password
            )
            
            return login_user_response(
                authenticated=authenticated,
                message=message,
                user=user,
                token=token
            )
        except Exception as e:
            self.logger.error(f"Error in login_user controller: {e}")
            return login_user_response(
                authenticated=False,
                message=f"Error during login: {str(e)}",
                user=None,
                token=None
            )
    
    async def get_user(self, email: str) -> get_user_response:
        """
        Get user information by email.
        
        Args:
            email: User's email
            
        Returns:
            get_user_response object
        """
        try:
            success, message, user = await self.users_service.get_user(email)
            return get_user_response(user=user, message=message)
        except Exception as e:
            self.logger.error(f"Error in get_user controller: {e}")
            return get_user_response(user=None, message=f"Error getting user: {str(e)}")
    
    async def register_fcm_token(
        self,
        request: register_fcm_token_request
    ) -> register_fcm_token_response:
        """
        Register FCM token for a user.
        
        Args:
            request: register_fcm_token_request object
            
        Returns:
            register_fcm_token_response object
        """
        try:
            success, message = await self.users_service.register_fcm_token(
                user_id=request.userId,
                fcm_token=request.fcmToken
            )
            return register_fcm_token_response(
                success=success,
                message=message
            )
        except Exception as e:
            self.logger.error(f"Error in register_fcm_token controller: {e}")
            return register_fcm_token_response(
                success=False,
                message=f"Error registering FCM token: {str(e)}"
            )
    
    async def unregister_fcm_token(
        self,
        request: unregister_fcm_token_request
    ) -> unregister_fcm_token_response:
        """
        Unregister FCM token for a user.
        
        Args:
            request: unregister_fcm_token_request object
            
        Returns:
            unregister_fcm_token_response object
        """
        try:
            success, message = await self.users_service.unregister_fcm_token(
                user_id=request.userId
            )
            return unregister_fcm_token_response(
                success=success,
                message=message
            )
        except Exception as e:
            self.logger.error(f"Error in unregister_fcm_token controller: {e}")
            return unregister_fcm_token_response(
                success=False,
                message=f"Error unregistering FCM token: {str(e)}"
            )

