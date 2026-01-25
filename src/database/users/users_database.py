"""Users database - Data access layer for PostgreSQL (BIGINT IDs)."""
from typing import Optional, List, Dict
from datetime import datetime
from uuid import uuid4
from src.utils.logger import get_logger
from src.utils.postgres_connection import PostgresConnection

class UsersDatabase:
    """Database layer for user operations using PostgreSQL with BIGINT IDs."""
    
    def __init__(self):
        """Initialize the database connection."""
        self.logger = get_logger(__name__)
        self.logger.info("UsersDatabase initialized successfully")
    
    async def create_user(
        self, 
        first_name: str, 
        last_name: str, 
        username: str, 
        email: str, 
        password_hash: str
    ) -> Optional[int]:
        """Create a new user in the database."""
        self.logger.debug(f"create_user called with username={username}, email={email}")
        
        connection = None
        try:
            connection = PostgresConnection.get_connection()
            cursor = connection.cursor()
            
            public_id = uuid4()
            query = """
                INSERT INTO users (public_id, first_name, last_name, username, email, password_hash)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id;
            """
            cursor.execute(query, (str(public_id), first_name, last_name, username, email, password_hash))
            user_id = cursor.fetchone()['id']
            connection.commit()
            
            self.logger.info(f"User created successfully with ID: {user_id}")
            return int(user_id)
        except Exception as e:
            if connection:
                connection.rollback()
            self.logger.error(f"Error creating user: {e}", exc_info=True)
            return None
        finally:
            if connection:
                PostgresConnection.return_connection(connection)

    async def get_user_by_email(self, email: str) -> Optional[dict]:
        """Get user by email."""
        self.logger.debug(f"get_user_by_email called with email={email}")
        return await self._get_user_by_field("email", email)

    async def get_user_by_id(self, user_id: int) -> Optional[dict]:
        """Get user by ID."""
        self.logger.debug(f"get_user_by_id called with user_id={user_id}")
        return await self._get_user_by_field("id", user_id)

    async def get_user_by_username(self, username: str) -> Optional[dict]:
        """Get user by username."""
        self.logger.debug(f"get_user_by_username called with username={username}")
        return await self._get_user_by_field("username", username)
    
    async def get_user_by_public_id(self, public_id: str) -> Optional[dict]:
        """Get user by public_id (UUID)."""
        self.logger.debug(f"get_user_by_public_id called with public_id={public_id}")
        return await self._get_user_by_field("public_id", public_id)

    async def _get_user_by_field(self, field: str, value: any) -> Optional[dict]:
        """Generic helper to fetch user by a specific field."""
        connection = None
        try:
            connection = PostgresConnection.get_connection()
            cursor = connection.cursor()
            
            query = f"SELECT * FROM users WHERE {field} = %s;"
            cursor.execute(query, (value,))
            user = cursor.fetchone()
            
            if user:
                # Convert results to dict if needed, already RealDictCursor
                user_dict = dict(user)
                # Ensure public_id is always a string (UUID)
                if 'public_id' in user_dict and user_dict['public_id']:
                    user_dict['public_id'] = str(user_dict['public_id'])
                return user_dict
            return None
        except Exception as e:
            self.logger.error(f"Error fetching user by {field}: {e}", exc_info=True)
            return None
        finally:
            if connection:
                PostgresConnection.return_connection(connection)

    async def register_fcm_token(self, user_id: int, fcm_token: str) -> bool:
        """Register or update FCM token for a user."""
        self.logger.debug(f"register_fcm_token called for user: {user_id}")
        
        connection = None
        try:
            connection = PostgresConnection.get_connection()
            cursor = connection.cursor()
            
            query = """
                UPDATE users 
                SET fcm_token = %s, fcm_token_updated = %s, updated_date = %s
                WHERE id = %s;
            """
            cursor.execute(query, (fcm_token, datetime.utcnow(), datetime.utcnow(), user_id))
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
        """Unregister FCM token for a user."""
        self.logger.debug(f"unregister_fcm_token called for user: {user_id}")
        
        connection = None
        try:
            connection = PostgresConnection.get_connection()
            cursor = connection.cursor()
            
            query = """
                UPDATE users 
                SET fcm_token = NULL, fcm_token_updated = NULL, updated_date = %s
                WHERE id = %s;
            """
            cursor.execute(query, (datetime.utcnow(), user_id))
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
        """Get FCM tokens for a list of user IDs."""
        self.logger.debug(f"get_fcm_tokens_for_users called with {len(user_ids)} IDs")
        
        if not user_ids:
            return {}
            
        connection = None
        try:
            connection = PostgresConnection.get_connection()
            cursor = connection.cursor()
            
            query = "SELECT id, fcm_token FROM users WHERE id = ANY(%s) AND fcm_token IS NOT NULL;"
            cursor.execute(query, (user_ids,))
            results = cursor.fetchall()
            
            tokens = {int(row['id']): row['fcm_token'] for row in results}
            self.logger.debug(f"Found {len(tokens)} FCM tokens")
            return tokens
        except Exception as e:
            self.logger.error(f"Error fetching FCM tokens: {e}", exc_info=True)
            return {}
        finally:
            if connection:
                PostgresConnection.return_connection(connection)
