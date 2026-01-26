from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

class User(BaseModel):
    """Model for a user."""
    public_id: str  # UUID (public-facing)
    first_name: str
    last_name: str
    username: str
    email: str
    created_date: datetime
    updated_date: datetime

class create_user_request(BaseModel):
    """Model for creating a new user."""
    first_name: str
    last_name: str
    username: str
    email: str
    password: str
    attended_churches: Optional[List[str]]
    
class create_user_response(BaseModel):
    """Model for creating a new user."""
    created: bool
    message: str

class login_user_request(BaseModel):
    """Model for logging in a user."""
    email: str
    password: str

class login_user_response(BaseModel):
    """Model for logging in a user."""
    authenticated: bool
    message: str
    user: Optional[User]
    token: Optional[str] = None

class get_user_request(BaseModel):
    """Model for getting user information."""
    email: str

class get_user_response(BaseModel):
    """Model for user information response."""
    user: Optional[User]
    message: str

class register_fcm_token_request(BaseModel):
    """Model for registering FCM token."""
    userId: str
    fcmToken: str

class register_fcm_token_response(BaseModel):
    """Model for FCM token registration response."""
    success: bool
    message: str

class unregister_fcm_token_request(BaseModel):
    """Model for unregistering FCM token."""
    userId: str

class unregister_fcm_token_response(BaseModel):
    """Model for FCM token unregistration response."""
    success: bool
    message: str