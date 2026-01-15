"""Users routes - HTTP layer."""
from fastapi import APIRouter, Query
from src.models.users import (
    create_user_request,
    create_user_response,
    login_user_request,
    login_user_response,
    get_user_response,
    register_fcm_token_request,
    register_fcm_token_response,
    unregister_fcm_token_request,
    unregister_fcm_token_response
)
from src.controller.users import UsersController

# Create a router for User-related routes
router = APIRouter()


@router.post("/create_user", response_model=create_user_response)
async def create_user(request: create_user_request):
    """
    Create a new user account.
    
    Request Body:
        first_name: User's first name
        last_name: User's last name
        username: Unique username
        email: Unique email address
        password: User's password
        attended_churches: Optional list of church IDs
    
    Returns:
        create_user_response with creation status and message
    """
    controller = UsersController()
    return await controller.create_user(
        first_name=request.first_name,
        last_name=request.last_name,
        username=request.username,
        email=request.email,
        password=request.password,
        attended_churches=request.attended_churches
    )


@router.post("/login", response_model=login_user_response)
async def login_user(request: login_user_request):
    """
    Authenticate a user and return a JWT token.
    
    Request Body:
        email: User's email address
        password: User's password
    
    Returns:
        login_user_response with authentication status, user info, and JWT token
    """
    controller = UsersController()
    return await controller.login_user(
        email=request.email,
        password=request.password
    )


@router.get("/get_user", response_model=get_user_response)
async def get_user(username: str = Query(..., description="The username of the user to retrieve")):
    """
    Get user information by username.
    
    Query Parameters:
        username: The username of the user to retrieve
    
    Returns:
        get_user_response with user information
    """
    controller = UsersController()
    return await controller.get_user(username=username)


@router.post("/register_fcm_token", response_model=register_fcm_token_response)
async def register_fcm_token(request: register_fcm_token_request):
    """
    Register FCM token for push notifications.
    
    Request Body:
        userId: User's ID
        fcmToken: Firebase Cloud Messaging token
    
    Returns:
        register_fcm_token_response with registration status
    """
    controller = UsersController()
    return await controller.register_fcm_token(request)


@router.post("/unregister_fcm_token", response_model=unregister_fcm_token_response)
async def unregister_fcm_token(request: unregister_fcm_token_request):
    """
    Unregister FCM token for a user.
    
    Request Body:
        userId: User's ID
    
    Returns:
        unregister_fcm_token_response with unregistration status
    """
    controller = UsersController()
    return await controller.unregister_fcm_token(request)
