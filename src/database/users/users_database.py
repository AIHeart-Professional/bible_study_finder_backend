"""Users database - Data access layer using Supabase HTTP API."""
from typing import Optional, List, Dict
from datetime import datetime
from src.utils.logger import get_logger
from src.utils.supabase_client import SupabaseClient


class UsersDatabase:
    """Database layer for user operations using Supabase HTTP API."""
    
    def __init__(self):
        """Initialize the database connection."""
        self.logger = get_logger(__name__)
        self.client = SupabaseClient.get_instance()
        self.logger.info("UsersDatabase initialized successfully (using Supabase HTTP API)")
    
    async def create_user(
        self, 
        first_name: str, 
        last_name: str, 
        username: str, 
        email: str, 
        password_hash: str
    ) -> Optional[str]:
        """
        Create a new user in Supabase auth.users.
        Note: Users should be created via Supabase Auth API, not directly.
        """
        self.logger.warning("create_user called - Supabase users should be created via Supabase Auth API")
        return None

    async def get_user_by_email(self, email: str) -> Optional[dict]:
        """Get user by email from Supabase auth.users."""
        self.logger.debug(f"get_user_by_email called with email={email}")
        
        try:
            results = await self.client.rpc("get_user_by_email", {"p_email": email})
            
            if results and len(results) > 0:
                return self._format_user_row(results[0])
            return None
            
        except Exception as e:
            self.logger.error(f"Error fetching user by email: {e}", exc_info=True)
            return None

    async def get_user_by_id(self, user_id) -> Optional[dict]:
        """Get user by ID from Supabase auth.users."""
        self.logger.debug(f"get_user_by_id called with user_id={user_id}")
        
        try:
            user_uuid = str(user_id)
            results = await self.client.rpc("get_user_by_id", {"p_user_id": user_uuid})
            
            if results and len(results) > 0:
                return self._format_user_row(results[0])
            return None
            
        except Exception as e:
            self.logger.error(f"Error fetching user by id: {e}", exc_info=True)
            return None
    
    async def get_user_by_public_id(self, public_id: str) -> Optional[dict]:
        """Get user by public_id (UUID) from Supabase auth.users."""
        self.logger.debug(f"get_user_by_public_id called with public_id={public_id}")
        return await self.get_user_by_id(public_id)
    
    async def get_user_by_username(self, username: str) -> Optional[dict]:
        """Get user by username from Supabase auth.users."""
        self.logger.debug(f"get_user_by_username called with username={username}")
        
        try:
            results = await self.client.rpc("get_user_by_username", {"p_username": username})
            
            if results and len(results) > 0:
                return self._format_user_row(results[0])
            return None
            
        except Exception as e:
            self.logger.error(f"Error fetching user by username: {e}", exc_info=True)
            return None

    def _format_user_row(self, row: dict) -> dict:
        """
        Format user row from RPC result to User model format.
        
        Args:
            row: Raw row from RPC result
        
        Returns:
            Formatted user dictionary
        """
        return {
            'public_id': str(row['public_id']),
            'email': row.get('email', ''),
            'first_name': row.get('first_name', ''),
            'last_name': row.get('last_name', ''),
            'username': row.get('username', ''),
            'created_date': row.get('created_date'),
            'updated_date': row.get('updated_date'),
            'raw_user_meta_data': row.get('raw_user_meta_data', {})
        }

    async def register_fcm_token(self, user_id, fcm_token: str) -> bool:
        """
        Register or update FCM token for a user.
        Note: This updates raw_user_meta_data in auth.users via Supabase Admin API.
        For production, consider using a separate table for FCM tokens.
        """
        self.logger.debug(f"register_fcm_token called for user: {user_id}")
        self.logger.warning("FCM token registration via HTTP API requires service_role key")
        
        # FCM token updates to auth.users require service_role key
        # For production, consider storing FCM tokens in a separate public table
        return False

    async def unregister_fcm_token(self, user_id) -> bool:
        """Unregister FCM token for a user."""
        self.logger.debug(f"unregister_fcm_token called for user: {user_id}")
        self.logger.warning("FCM token unregistration via HTTP API requires service_role key")
        
        # FCM token updates to auth.users require service_role key
        return False

    async def get_fcm_tokens_for_users(self, user_ids: List) -> Dict:
        """Get FCM tokens for a list of user IDs."""
        self.logger.debug(f"get_fcm_tokens_for_users called with {len(user_ids)} IDs")
        
        if not user_ids:
            return {}
        
        try:
            user_uuids = [str(uid) for uid in user_ids]
            results = await self.client.rpc("get_fcm_tokens_for_users", {"p_user_ids": user_uuids})
            
            tokens = {}
            for row in results:
                user_uuid = str(row['user_id'])
                fcm_token = row.get('fcm_token')
                if fcm_token:
                    # Find matching original user_id
                    for orig_id in user_ids:
                        if str(orig_id) == user_uuid:
                            tokens[orig_id] = fcm_token
                            break
            
            self.logger.debug(f"Found {len(tokens)} FCM tokens")
            return tokens
            
        except Exception as e:
            self.logger.error(f"Error fetching FCM tokens: {e}", exc_info=True)
            return {}
