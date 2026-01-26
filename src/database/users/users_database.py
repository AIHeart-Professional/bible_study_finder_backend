"""Users database - Data access layer for Supabase auth.users."""
from typing import Optional, List, Dict
from datetime import datetime
from uuid import UUID
from src.utils.logger import get_logger
from src.utils.postgres_connection import PostgresConnection

class UsersDatabase:
    """Database layer for user operations using Supabase auth.users table."""
    
    def __init__(self):
        """Initialize the database connection."""
        self.logger = get_logger(__name__)
        self.logger.info("UsersDatabase initialized successfully (using Supabase auth.users)")
    
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
        Note: This should typically be done via Supabase Auth API, not directly in the database.
        This method is kept for backward compatibility but may not work with Supabase's auth system.
        """
        self.logger.warning("create_user called - Supabase users should be created via Supabase Auth API")
        self.logger.debug(f"create_user called with username={username}, email={email}")
        # Supabase handles user creation through their Auth API
        # This method should not be used with Supabase - users are created via Supabase Auth
        return None

    async def get_user_by_email(self, email: str) -> Optional[dict]:
        """Get user by email from Supabase auth.users."""
        self.logger.debug(f"get_user_by_email called with email={email}")
        return await self._get_user_from_auth_users("email", email)

    async def get_user_by_id(self, user_id: int) -> Optional[dict]:
        """
        Get user by ID from Supabase auth.users.
        Note: Supabase uses UUID, not BIGINT. This method accepts int for backward compatibility
        but will convert it to UUID string.
        """
        self.logger.debug(f"get_user_by_id called with user_id={user_id}")
        # Convert int to UUID string if needed
        user_uuid = str(user_id) if isinstance(user_id, (int, str)) else user_id
        return await self._get_user_from_auth_users("id", user_uuid)
    
    async def get_user_by_public_id(self, public_id: str) -> Optional[dict]:
        """
        Get user by public_id (UUID) from Supabase auth.users.
        In Supabase, the id IS the public_id (UUID).
        """
        self.logger.debug(f"get_user_by_public_id called with public_id={public_id}")
        return await self._get_user_from_auth_users("id", public_id)
    
    async def get_user_by_username(self, username: str) -> Optional[dict]:
        """
        Get user by username from Supabase auth.users.
        Username is stored in raw_user_meta_data JSONB field.
        """
        self.logger.debug(f"get_user_by_username called with username={username}")
        return await self._get_user_by_username_from_auth(username)

    async def _get_user_from_auth_users(self, field: str, value: any) -> Optional[dict]:
        """
        Generic helper to fetch user from Supabase auth.users table.
        Maps Supabase schema to our User model format.
        """
        connection = None
        try:
            connection = PostgresConnection.get_connection()
            cursor = connection.cursor()
            
            # Query Supabase auth.users table
            query = f"""
                SELECT 
                    id,
                    email,
                    raw_user_meta_data,
                    created_at,
                    updated_at
                FROM auth.users 
                WHERE {field} = %s;
            """
            cursor.execute(query, (value,))
            user = cursor.fetchone()
            
            if user:
                user_dict = dict(user)
                # Map Supabase fields to our User model format
                # id (UUID) is the public_id
                user_dict['public_id'] = str(user_dict['id'])
                
                # Extract custom fields from raw_user_meta_data JSONB
                meta_data = user_dict.get('raw_user_meta_data', {}) or {}
                # Handle first_name - use first_name from meta_data, or extract from name/full_name
                user_dict['first_name'] = meta_data.get('first_name', '') or (meta_data.get('name', '').split()[0] if meta_data.get('name') else '') or (meta_data.get('full_name', '').split()[0] if meta_data.get('full_name') else '')
                # Handle last_name - use last_name from meta_data, or extract from name/full_name
                user_dict['last_name'] = meta_data.get('last_name', '') or (' '.join(meta_data.get('name', '').split()[1:]) if meta_data.get('name') and len(meta_data.get('name', '').split()) > 1 else '') or (' '.join(meta_data.get('full_name', '').split()[1:]) if meta_data.get('full_name') and len(meta_data.get('full_name', '').split()) > 1 else '')
                # Username doesn't exist in Supabase - derive from name, full_name, or email prefix
                user_dict['username'] = meta_data.get('name') or meta_data.get('full_name') or (user_dict.get('email', '').split('@')[0] if user_dict.get('email') else '')
                
                # Map timestamps
                user_dict['created_date'] = user_dict.get('created_at')
                user_dict['updated_date'] = user_dict.get('updated_at')
                
                return user_dict
            return None
        except Exception as e:
            self.logger.error(f"Error fetching user by {field} from auth.users: {e}", exc_info=True)
            return None
        finally:
            if connection:
                PostgresConnection.return_connection(connection)
    
    async def _get_user_by_username_from_auth(self, username: str) -> Optional[dict]:
        """
        Get user by username from Supabase auth.users.
        Note: username doesn't exist in Supabase, so we search by name, full_name, or email prefix.
        """
        connection = None
        try:
            connection = PostgresConnection.get_connection()
            cursor = connection.cursor()
            
            # Query Supabase auth.users table - search by name, full_name, or email prefix
            # Since username doesn't exist, we match against name/full_name or email prefix
            query = """
                SELECT 
                    id,
                    email,
                    raw_user_meta_data,
                    created_at,
                    updated_at
                FROM auth.users 
                WHERE raw_user_meta_data->>'name' = %s
                   OR raw_user_meta_data->>'full_name' = %s
                   OR SPLIT_PART(email, '@', 1) = %s
                LIMIT 1;
            """
            cursor.execute(query, (username, username, username))
            user = cursor.fetchone()
            
            if user:
                user_dict = dict(user)
                # Map Supabase fields to our User model format
                user_dict['public_id'] = str(user_dict['id'])
                
                # Extract custom fields from raw_user_meta_data JSONB
                meta_data = user_dict.get('raw_user_meta_data', {}) or {}
                # Handle first_name - use first_name from meta_data, or extract from name/full_name
                user_dict['first_name'] = meta_data.get('first_name', '') or (meta_data.get('name', '').split()[0] if meta_data.get('name') else '') or (meta_data.get('full_name', '').split()[0] if meta_data.get('full_name') else '')
                # Handle last_name - use last_name from meta_data, or extract from name/full_name
                user_dict['last_name'] = meta_data.get('last_name', '') or (' '.join(meta_data.get('name', '').split()[1:]) if meta_data.get('name') and len(meta_data.get('name', '').split()) > 1 else '') or (' '.join(meta_data.get('full_name', '').split()[1:]) if meta_data.get('full_name') and len(meta_data.get('full_name', '').split()) > 1 else '')
                # Username doesn't exist in Supabase - derive from name, full_name, or email prefix
                user_dict['username'] = meta_data.get('name') or meta_data.get('full_name') or (user_dict.get('email', '').split('@')[0] if user_dict.get('email') else '')
                
                # Map timestamps
                user_dict['created_date'] = user_dict.get('created_at')
                user_dict['updated_date'] = user_dict.get('updated_at')
                
                return user_dict
            return None
        except Exception as e:
            self.logger.error(f"Error fetching user by username from auth.users: {e}", exc_info=True)
            return None
        finally:
            if connection:
                PostgresConnection.return_connection(connection)

    async def register_fcm_token(self, user_id: int, fcm_token: str) -> bool:
        """
        Register or update FCM token for a user.
        Note: With Supabase, you may want to store FCM tokens in a separate table
        or in raw_user_meta_data. This implementation updates raw_user_meta_data.
        """
        self.logger.debug(f"register_fcm_token called for user: {user_id}")
        
        connection = None
        try:
            connection = PostgresConnection.get_connection()
            cursor = connection.cursor()
            
            # Get current user data
            user_uuid = str(user_id) if isinstance(user_id, int) else user_id
            user_data = await self._get_user_from_auth_users("id", user_uuid)
            
            if not user_data:
                self.logger.warning(f"User {user_id} not found for FCM token registration")
                return False
            
            # Update raw_user_meta_data with FCM token
            meta_data = user_data.get('raw_user_meta_data', {}) or {}
            meta_data['fcm_token'] = fcm_token
            meta_data['fcm_token_updated'] = datetime.utcnow().isoformat()
            
            query = """
                UPDATE auth.users 
                SET raw_user_meta_data = %s, updated_at = %s
                WHERE id = %s;
            """
            cursor.execute(query, (meta_data, datetime.utcnow(), user_uuid))
            connection.commit()
            
            success = cursor.rowcount > 0
            if success:
                self.logger.info(f"FCM token registered successfully for user: {user_id}")
            return success
        except Exception as e:
            if connection:
                connection.rollback()
            self.logger.error(f"Error registering FCM token: {e}", exc_info=True)
            return False
        finally:
            if connection:
                PostgresConnection.return_connection(connection)

    async def unregister_fcm_token(self, user_id: int) -> bool:
        """Unregister FCM token for a user from Supabase auth.users."""
        self.logger.debug(f"unregister_fcm_token called for user: {user_id}")
        
        connection = None
        try:
            connection = PostgresConnection.get_connection()
            cursor = connection.cursor()
            
            # Get current user data
            user_uuid = str(user_id) if isinstance(user_id, int) else user_id
            user_data = await self._get_user_from_auth_users("id", user_uuid)
            
            if not user_data:
                self.logger.warning(f"User {user_id} not found for FCM token unregistration")
                return False
            
            # Remove FCM token from raw_user_meta_data
            meta_data = user_data.get('raw_user_meta_data', {}) or {}
            meta_data.pop('fcm_token', None)
            meta_data.pop('fcm_token_updated', None)
            
            query = """
                UPDATE auth.users 
                SET raw_user_meta_data = %s, updated_at = %s
                WHERE id = %s;
            """
            cursor.execute(query, (meta_data, datetime.utcnow(), user_uuid))
            connection.commit()
            
            success = cursor.rowcount > 0
            if success:
                self.logger.info(f"FCM token unregistered successfully for user: {user_id}")
            return success
        except Exception as e:
            if connection:
                connection.rollback()
            self.logger.error(f"Error unregistering FCM token: {e}", exc_info=True)
            return False
        finally:
            if connection:
                PostgresConnection.return_connection(connection)

    async def get_fcm_tokens_for_users(self, user_ids: List[int]) -> Dict[int, str]:
        """
        Get FCM tokens for a list of user IDs from Supabase auth.users.
        Note: user_ids can be int (for backward compatibility) or UUID strings.
        """
        self.logger.debug(f"get_fcm_tokens_for_users called with {len(user_ids)} IDs")
        
        if not user_ids:
            return {}
            
        connection = None
        try:
            connection = PostgresConnection.get_connection()
            cursor = connection.cursor()
            
            # Convert user_ids to UUID strings for querying
            user_uuids = [str(uid) if isinstance(uid, int) else uid for uid in user_ids]
            
            # Query Supabase auth.users and extract FCM token from raw_user_meta_data
            query = """
                SELECT 
                    id,
                    raw_user_meta_data->>'fcm_token' as fcm_token
                FROM auth.users 
                WHERE id = ANY(%s::uuid[]) 
                AND raw_user_meta_data->>'fcm_token' IS NOT NULL;
            """
            cursor.execute(query, (user_uuids,))
            results = cursor.fetchall()
            
            # Map results back to original user_ids format
            tokens = {}
            for row in results:
                user_uuid = str(row['id'])
                fcm_token = row.get('fcm_token')
                if fcm_token:
                    # Find matching original user_id (int or UUID string)
                    for orig_id in user_ids:
                        if str(orig_id) == user_uuid:
                            tokens[orig_id] = fcm_token
                            break
            
            self.logger.debug(f"Found {len(tokens)} FCM tokens")
            return tokens
        except Exception as e:
            self.logger.error(f"Error fetching FCM tokens: {e}", exc_info=True)
            return {}
        finally:
            if connection:
                PostgresConnection.return_connection(connection)
