"""Groups database - Data access layer for PostgreSQL (BIGINT IDs)."""
import io
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime
from uuid import UUID
from fastapi import UploadFile
from fastapi.responses import StreamingResponse
from src.utils.logger import get_logger
from src.utils.postgres_connection import PostgresConnection
from src.utils.text_extractor import TextExtractor
from psycopg2.extras import Json

class GroupsDatabase:
    """Database layer for group operations using PostgreSQL with BIGINT IDs."""
    
    def __init__(self):
        """Initialize the database connection."""
        self.logger = get_logger(__name__)
        self.logger.info("GroupsDatabase initialized successfully")

    async def _resolve_user_id_from_public_id(self, public_id: str) -> Optional[str]:
        """
        Resolve user's public_id (UUID) to UUID string for Supabase auth.users.
        In Supabase, the id IS the public_id (UUID), so we just validate and return it.
        Note: Returns UUID string, not BIGINT, since Supabase uses UUID.
        """
        self.logger.debug(f"_resolve_user_id_from_public_id called with public_id={public_id}")
        
        try:
            # Validate UUID format
            UUID(public_id)
            # In Supabase, public_id is the same as id (UUID)
            self.logger.debug(f"Using public_id {public_id} as user UUID")
            return public_id
        except ValueError:
            self.logger.error(f"Invalid UUID format: {public_id}")
            return None

    async def create_group(
        self,
        name: str,
        description: str,
        leaderPublicId: str,
        location: dict,
        meetingStartTime: Optional[datetime] = None,
        meetingEndTime: Optional[datetime] = None,
        genderFocus: Optional[str] = None,
        meetingDays: Optional[List[str]] = None,
        demographic: Optional[str] = None,
        groupType: Optional[str] = None,
        meetingConsistency: Optional[str] = None,
        meetingFormat: Optional[str] = None,
        status: Optional[str] = None
    ) -> Optional[str]:
        """
        Create a new group in the database.
        Note: leader_user_id is now UUID (from Supabase auth.users).
        """
        self.logger.debug(f"create_group called with name={name}, leaderPublicId={leaderPublicId}")
        
        # Resolve public_id to UUID (Supabase uses UUID as id)
        leader_user_id = await self._resolve_user_id_from_public_id(leaderPublicId)
        if not leader_user_id:
            self.logger.error(f"Failed to resolve leader public_id: {leaderPublicId}")
            return None
        
        connection = None
        try:
            connection = PostgresConnection.get_connection()
            cursor = connection.cursor()
            
            # Build query with all fields
            # PostgreSQL will handle NULL values correctly with enum casting
            query = """
                INSERT INTO groups (
                    name, description, leader_user_id, location,
                    meeting_start_time, meeting_end_time,
                    gender_focus, meeting_days, demographic,
                    group_type, meeting_consistency, meeting_format, status
                )
                VALUES (
                    %s, %s, %s::uuid, %s,
                    %s, %s,
                    %s::gender_focus, %s::days, %s::demographic,
                    %s::group_types, %s::meeting_consistency, %s::meeting_type, %s::status
                )
                RETURNING public_id;
            """
            cursor.execute(query, (
                name, description, leader_user_id, Json(location),
                meetingStartTime, meetingEndTime,
                genderFocus, meetingDays, demographic,
                groupType, meetingConsistency, meetingFormat, status
            ))
            group_public_id = cursor.fetchone()['public_id']
            connection.commit()
            self.logger.info(f"Group created successfully with public_id: {group_public_id}")
            return str(group_public_id)
        except Exception as e:
            if connection: connection.rollback()
            self.logger.error(f"Error creating group: {e}", exc_info=True)
            return None
        finally:
            if connection: PostgresConnection.return_connection(connection)
    
    async def _resolve_group_id_from_public_id(self, public_id: str) -> Optional[int]:
        """Resolve group's public_id (UUID) to internal id (BIGINT)."""
        self.logger.debug(f"_resolve_group_id_from_public_id called with public_id={public_id}")
        
        connection = None
        try:
            # Validate UUID format
            try:
                UUID(public_id)
            except ValueError:
                self.logger.error(f"Invalid UUID format: {public_id}")
                return None
            
            connection = PostgresConnection.get_connection()
            cursor = connection.cursor()
            
            query = "SELECT id FROM groups WHERE public_id = %s;"
            cursor.execute(query, (public_id,))
            result = cursor.fetchone()
            
            if result:
                group_id = int(result['id'])
                self.logger.debug(f"Resolved group public_id {public_id} to internal id {group_id}")
                return group_id
            else:
                self.logger.warning(f"Group with public_id {public_id} not found")
                return None
        except Exception as e:
            self.logger.error(f"Error resolving group_id from public_id: {e}", exc_info=True)
            return None
        finally:
            if connection:
                PostgresConnection.return_connection(connection)
    
    async def _resolve_user_public_id_from_user_id(self, user_id: int) -> Optional[str]:
        """
        Resolve user's internal id to public_id (UUID).
        With Supabase, if user_id is already a UUID string, return it.
        If it's an int (BIGINT from old schema), we need to look it up.
        Note: This method handles backward compatibility with BIGINT user_ids.
        """
        self.logger.debug(f"_resolve_user_public_id_from_user_id called with user_id={user_id}")
        
        # If user_id is already a string (UUID), return it
        if isinstance(user_id, str):
            try:
                UUID(user_id)
                return user_id
            except ValueError:
                pass
        
        # If user_id is int, we need to check if groups table still uses BIGINT
        # For now, treat int as UUID string (may need adjustment based on your schema)
        connection = None
        try:
            connection = PostgresConnection.get_connection()
            cursor = connection.cursor()
            
            # Try to find user by converting int to UUID string
            # This assumes your groups table might still reference old users table
            # You may need to adjust this based on your actual schema migration
            query = "SELECT id FROM auth.users WHERE id::text = %s;"
            cursor.execute(query, (str(user_id),))
            result = cursor.fetchone()
            
            if result:
                public_id = str(result['id'])
                self.logger.debug(f"Resolved user_id {user_id} to public_id {public_id}")
                return public_id
            else:
                self.logger.warning(f"User with id {user_id} not found")
                return None
        except Exception as e:
            self.logger.error(f"Error resolving user public_id from user_id: {e}", exc_info=True)
            return None
        finally:
            if connection:
                PostgresConnection.return_connection(connection)
    
    async def _resolve_group_public_id_from_group_id(self, group_id: int) -> Optional[str]:
        """Resolve group's internal id (BIGINT) to public_id (UUID)."""
        self.logger.debug(f"_resolve_group_public_id_from_group_id called with group_id={group_id}")
        
        connection = None
        try:
            connection = PostgresConnection.get_connection()
            cursor = connection.cursor()
            
            query = "SELECT public_id FROM groups WHERE id = %s;"
            cursor.execute(query, (group_id,))
            result = cursor.fetchone()
            
            if result and result.get('public_id'):
                public_id = str(result['public_id'])
                self.logger.debug(f"Resolved group_id {group_id} to public_id {public_id}")
                return public_id
            else:
                self.logger.warning(f"Group with id {group_id} not found or has no public_id")
                return None
        except Exception as e:
            self.logger.error(f"Error resolving group public_id from group_id: {e}", exc_info=True)
            return None
        finally:
            if connection:
                PostgresConnection.return_connection(connection)

    async def initialize_group(self, groupPublicId: str) -> bool:
        """Initialize a group with empty study plans and meals."""
        self.logger.debug(f"initialize_group called with groupPublicId={groupPublicId}")
        
        # Resolve public_id to internal id
        group_id = await self._resolve_group_id_from_public_id(groupPublicId)
        if not group_id:
            self.logger.error(f"Failed to resolve group public_id: {groupPublicId}")
            return False
        
        connection = None
        try:
            connection = PostgresConnection.get_connection()
            cursor = connection.cursor()
            query = "UPDATE groups SET study_plans = '[]'::jsonb, meals = '[]'::jsonb, updated_at = %s WHERE id = %s;"
            cursor.execute(query, (datetime.utcnow(), group_id))
            connection.commit()
            return cursor.rowcount > 0
        except Exception as e:
            if connection: connection.rollback()
            self.logger.error(f"Error initializing group: {e}", exc_info=True)
            return False
        finally:
            if connection: PostgresConnection.return_connection(connection)

    async def get_all_groups(self) -> List[dict]:
        """Get all groups from the database."""
        connection = None
        try:
            connection = PostgresConnection.get_connection()
            cursor = connection.cursor()
            # Use JOIN to get leader public_id and username in one query
            query = """
                SELECT 
                    g.id,
                    g.public_id,
                    g.name,
                    g.description,
                    g.leader_user_id,
                    g.location,
                    g.image,
                    g.study_plans,
                    g.meals,
                    g.meeting_consistency,
                    g.status,
                    g.meeting_days,
                    g.meeting_start_time,
                    g.meeting_end_time,
                    g.gender_focus,
                    g.demographic,
                    g.group_type,
                    g.meeting_format,
                    g.created_at,
                    g.updated_at,
                    u.id as leader_public_id,
                    COALESCE(
                        u.raw_user_meta_data->>'name',
                        u.raw_user_meta_data->>'full_name',
                        SPLIT_PART(u.email, '@', 1)
                    ) as leader_username
                FROM groups g
                LEFT JOIN auth.users u ON g.leader_user_id::uuid = u.id
                ORDER BY g.created_at DESC;
            """
            cursor.execute(query)
            results = cursor.fetchall()
            formatted_results = []
            for row in results:
                formatted_row = self._format_group_row(row)
                formatted_results.append(formatted_row)
            return formatted_results
        except Exception as e:
            self.logger.error(f"Error in get_all_groups: {e}", exc_info=True)
            return []
        finally:
            if connection: PostgresConnection.return_connection(connection)

    def _format_group_row(self, row: dict) -> dict:
        """Format group database row to dictionary."""
        row['id'] = int(row['id'])
        if row.get('public_id'):
            row['public_id'] = str(row['public_id'])
        if row.get('leader_public_id'):
            row['leaderUserId'] = str(row['leader_public_id'])
        elif row.get('leader_user_id'):
            # Fallback if JOIN didn't work
            row['leaderUserId'] = str(row['leader_user_id'])
        row['leaderUsername'] = row.get('leader_username')
        row['createdAt'] = row['created_at']
        row['updatedAt'] = row['updated_at']
        row['studyPlans'] = row.get('study_plans', [])
        row['meals'] = row.get('meals', [])
        row['meetingConsistency'] = row.get('meeting_consistency')
        row['status'] = row.get('status')
        # Convert meeting_days to list if it's a string or array
        meeting_days = row.get('meeting_days')
        if meeting_days is None:
            row['meetingDays'] = []
        elif isinstance(meeting_days, str):
            # If it's a single string, convert to list
            # Handle both plain strings and JSON strings
            try:
                import json
                parsed = json.loads(meeting_days)
                row['meetingDays'] = parsed if isinstance(parsed, list) else [parsed] if parsed else []
            except (json.JSONDecodeError, TypeError):
                # If it's not JSON, treat as a single day string
                row['meetingDays'] = [meeting_days] if meeting_days else []
        elif isinstance(meeting_days, list):
            row['meetingDays'] = meeting_days
        else:
            # Handle other types (e.g., PostgreSQL array types, tuples)
            try:
                row['meetingDays'] = list(meeting_days) if meeting_days else []
            except (TypeError, ValueError):
                row['meetingDays'] = []
        row['meetingStartTime'] = row.get('meeting_start_time')
        row['meetingEndTime'] = row.get('meeting_end_time')
        row['genderFocus'] = row.get('gender_focus')
        row['demographic'] = row.get('demographic')
        row['groupType'] = row.get('group_type')
        row['meetingFormat'] = row.get('meeting_format')
        return row

    async def get_group_by_public_id(self, public_id: str) -> Optional[dict]:
        """Get group by public_id (UUID)."""
        self.logger.debug(f"get_group_by_public_id called with public_id={public_id}")
        
        # Resolve public_id to internal id
        group_id = await self._resolve_group_id_from_public_id(public_id)
        if not group_id:
            self.logger.warning(f"Group with public_id {public_id} not found")
            return None
        
        return await self.get_group_by_id(group_id)

    async def get_group_by_id(self, groupId: int) -> Optional[dict]:
        """Get group by internal ID."""
        connection = None
        try:
            connection = PostgresConnection.get_connection()
            cursor = connection.cursor()
            # Use JOIN to get leader public_id and username in one query
            query = """
                SELECT 
                    g.id,
                    g.public_id,
                    g.name,
                    g.description,
                    g.leader_user_id,
                    g.location,
                    g.image,
                    g.study_plans,
                    g.meals,
                    g.meeting_consistency,
                    g.status,
                    g.meeting_days,
                    g.meeting_start_time,
                    g.meeting_end_time,
                    g.gender_focus,
                    g.demographic,
                    g.group_type,
                    g.meeting_format,
                    g.created_at,
                    g.updated_at,
                    u.id as leader_public_id,
                    COALESCE(
                        u.raw_user_meta_data->>'name',
                        u.raw_user_meta_data->>'full_name',
                        SPLIT_PART(u.email, '@', 1)
                    ) as leader_username
                FROM groups g
                LEFT JOIN auth.users u ON g.leader_user_id::uuid = u.id
                WHERE g.id = %s;
            """
            cursor.execute(query, (groupId,))
            row = cursor.fetchone()
            return self._format_group_row(row) if row else None
        except Exception as e:
            self.logger.error(f"Error in get_group_by_id: {e}", exc_info=True)
            return None
        finally:
            if connection: PostgresConnection.return_connection(connection)

    async def get_group_members(self, groupPublicId: str) -> List[dict]:
        """Get all members of a group with role information."""
        self.logger.debug(f"get_group_members called with groupPublicId={groupPublicId}")
        
        # Resolve public_id to internal id
        group_id = await self._resolve_group_id_from_public_id(groupPublicId)
        if not group_id:
            self.logger.warning(f"Group with public_id {groupPublicId} not found")
            return []
        
        connection = None
        try:
            connection = PostgresConnection.get_connection()
            cursor = connection.cursor()
            # Use JOIN to get user public_id and user details in one query
            query = """
                SELECT 
                    gm.id,
                    gm.group_id,
                    gm.user_id,
                    gm.joined_at,
                    grc.role_name as role,
                    grc.permissions,
                    u.id as user_public_id,
                    COALESCE(
                        u.raw_user_meta_data->>'name',
                        u.raw_user_meta_data->>'full_name',
                        SPLIT_PART(u.email, '@', 1)
                    ) as username,
                    u.email
                FROM group_memberships gm
                LEFT JOIN group_role_configs grc ON gm.group_role_id = grc.id
                LEFT JOIN auth.users u ON gm.user_id::uuid = u.id
                WHERE gm.group_id = %s;
            """
            cursor.execute(query, (group_id,))
            results = cursor.fetchall()
            self.logger.debug(f"Found {len(results)} members for group_id {group_id}")
            formatted_results = []
            for row in results:
                formatted_row = self._format_membership_row(row)
                formatted_results.append(formatted_row)
            return formatted_results
        except Exception as e:
            self.logger.error(f"Error in get_group_members: {e}", exc_info=True)
            return []
        finally:
            if connection: PostgresConnection.return_connection(connection)

    def _format_membership_row(self, row: dict) -> dict:
        """Format membership row."""
        row['id'] = int(row['id'])
        row['groupId'] = int(row['group_id'])
        # Use public_id from JOIN
        if row.get('user_public_id'):
            row['userId'] = str(row['user_public_id'])
        elif row.get('user_id'):
            row['userId'] = str(row['user_id'])  # Fallback
        # Include user details from JOIN
        row['username'] = row.get('username', '')
        row['email'] = row.get('email', '')
        row['portraitUrl'] = None  # Users table doesn't have portrait_url column
        row['joinedAt'] = row['joined_at']
        row['role'] = row.get('role', 'member') or 'member'
        row['permissions'] = row.get('permissions', []) or []
        return row

    async def get_group_meals(self, groupPublicId: str) -> List[dict]:
        """Get all meals for a group (from JSONB field)."""
        self.logger.debug(f"get_group_meals called with groupPublicId={groupPublicId}")
        
        # Resolve public_id to internal id
        group_id = await self._resolve_group_id_from_public_id(groupPublicId)
        if not group_id:
            self.logger.warning(f"Group with public_id {groupPublicId} not found")
            return []
        
        connection = None
        try:
            connection = PostgresConnection.get_connection()
            cursor = connection.cursor()
            cursor.execute("SELECT meals FROM groups WHERE id = %s;", (group_id,))
            row = cursor.fetchone()
            if row and row.get('meals'):
                return row['meals'] if isinstance(row['meals'], list) else []
            return []
        finally:
            if connection: PostgresConnection.return_connection(connection)
    
    async def get_group_study_plans(self, groupPublicId: str) -> List[dict]:
        """Get all study plans for a group (from JSONB field)."""
        self.logger.debug(f"get_group_study_plans called with groupPublicId={groupPublicId}")
        
        # Resolve public_id to internal id
        group_id = await self._resolve_group_id_from_public_id(groupPublicId)
        if not group_id:
            self.logger.warning(f"Group with public_id {groupPublicId} not found")
            return []
        
        connection = None
        try:
            connection = PostgresConnection.get_connection()
            cursor = connection.cursor()
            cursor.execute("SELECT study_plans FROM groups WHERE id = %s;", (group_id,))
            row = cursor.fetchone()
            if row and row.get('study_plans'):
                return row['study_plans'] if isinstance(row['study_plans'], list) else []
            return []
        finally:
            if connection: PostgresConnection.return_connection(connection)

    async def get_group_chats(self, groupPublicId: str) -> List[dict]:
        """Get all chat messages for a group."""
        self.logger.debug(f"get_group_chats called with groupPublicId={groupPublicId}")
        
        # Resolve public_id to internal id
        group_id = await self._resolve_group_id_from_public_id(groupPublicId)
        if not group_id:
            self.logger.warning(f"Group with public_id {groupPublicId} not found")
            return []
        
        connection = None
        try:
            connection = PostgresConnection.get_connection()
            cursor = connection.cursor()
            # Use JOIN to get user public_id and username in one query
            query = """
                SELECT 
                    gc.id,
                    gc.group_id,
                    gc.user_id,
                    gc.message,
                    gc.sent_at,
                    u.id as user_public_id,
                    COALESCE(
                        u.raw_user_meta_data->>'name',
                        u.raw_user_meta_data->>'full_name',
                        SPLIT_PART(u.email, '@', 1)
                    ) as username
                FROM group_chats gc
                LEFT JOIN auth.users u ON gc.user_id::uuid = u.id
                WHERE gc.group_id = %s
                ORDER BY gc.sent_at ASC;
            """
            cursor.execute(query, (group_id,))
            results = cursor.fetchall()
            self.logger.debug(f"Found {len(results)} chat messages for group_id {group_id}")
            formatted_results = []
            for r in results:
                formatted = {
                    'id': int(r['id']),
                    'groupId': int(r['group_id']),
                    'userId': str(r['user_public_id']) if r.get('user_public_id') else str(r['user_id']),
                    'username': r.get('username', ''),
                    'message': r.get('message', ''),
                    'sentAt': r['sent_at']
                }
                formatted_results.append(formatted)
            return formatted_results
        except Exception as e:
            self.logger.error(f"Error in get_group_chats: {e}", exc_info=True)
            return []
        finally:
            if connection: PostgresConnection.return_connection(connection)

    async def create_group_chat(self, groupPublicId: str, userPublicId: str, message: str) -> Optional[int]:
        """Create a new group chat message."""
        self.logger.debug(f"create_group_chat called with groupPublicId={groupPublicId}, userPublicId={userPublicId}")
        
        # Resolve public_ids to internal ids
        group_id = await self._resolve_group_id_from_public_id(groupPublicId)
        user_id = await self._resolve_user_id_from_public_id(userPublicId)
        
        if not group_id:
            self.logger.error(f"Failed to resolve group public_id: {groupPublicId}")
            return None
        if not user_id:
            self.logger.error(f"Failed to resolve user public_id: {userPublicId}")
            return None
        
        connection = None
        try:
            connection = PostgresConnection.get_connection()
            cursor = connection.cursor()
            cursor.execute("INSERT INTO group_chats (group_id, user_id, message) VALUES (%s, %s, %s) RETURNING id;", (group_id, user_id, message))
            chat_id = cursor.fetchone()['id']
            connection.commit()
            self.logger.info(f"Group chat created successfully with ID: {chat_id}")
            return int(chat_id)
        except Exception as e:
            if connection: connection.rollback()
            self.logger.error(f"Error creating group chat: {e}", exc_info=True)
            return None
        finally:
            if connection: PostgresConnection.return_connection(connection)

    async def create_worksheet(self, groupPublicId: str, title: str, content: str) -> Optional[int]:
        """Create a new Bible worksheet."""
        self.logger.debug(f"create_worksheet called with groupPublicId={groupPublicId}")
        
        # Resolve public_id to internal id
        group_id = await self._resolve_group_id_from_public_id(groupPublicId)
        if not group_id:
            self.logger.error(f"Failed to resolve group public_id: {groupPublicId}")
            return None
        
        connection = None
        try:
            connection = PostgresConnection.get_connection()
            cursor = connection.cursor()
            query = "INSERT INTO bible_worksheets (group_id, title, content) VALUES (%s, %s, %s) RETURNING id;"
            cursor.execute(query, (group_id, title, content))
            ws_id = cursor.fetchone()['id']
            connection.commit()
            self.logger.info(f"Worksheet created successfully with ID: {ws_id}")
            return int(ws_id)
        except Exception as e:
            if connection: connection.rollback()
            self.logger.error(f"Error creating worksheet: {e}", exc_info=True)
            return None
        finally:
            if connection: PostgresConnection.return_connection(connection)

    async def get_group_worksheets(self, groupPublicId: str) -> List[dict]:
        """Get all worksheets for a group."""
        self.logger.debug(f"get_group_worksheets called with groupPublicId={groupPublicId}")
        
        # Resolve public_id to internal id
        group_id = await self._resolve_group_id_from_public_id(groupPublicId)
        if not group_id:
            self.logger.warning(f"Group with public_id {groupPublicId} not found")
            return []
        
        connection = None
        try:
            connection = PostgresConnection.get_connection()
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM bible_worksheets WHERE group_id = %s ORDER BY created_at DESC;", (group_id,))
            results = cursor.fetchall()
            for r in results:
                r['id'] = int(r['id'])
                r['groupId'] = int(r['group_id'])
                r['createdAt'] = r['created_at']
            return results
        finally:
            if connection: PostgresConnection.return_connection(connection)

    async def upload_worksheet_file(self, groupPublicId: str, title: str, file: UploadFile, file_type: str) -> tuple:
        """Upload a worksheet file."""
        self.logger.debug(f"upload_worksheet_file called with groupPublicId={groupPublicId}")
        
        # Resolve public_id to internal id
        group_id = await self._resolve_group_id_from_public_id(groupPublicId)
        if not group_id:
            self.logger.error(f"Failed to resolve group public_id: {groupPublicId}")
            return (False, f"Group not found", None, None, None, None)
        
        try:
            content = await file.read()
            file_id = await self._store_file_in_postgres(file.filename, file.content_type, content)
            extracted = await TextExtractor.extract_text(content, file_type)
            ws_id = await self._create_worksheet_entry(group_id, title, extracted, file_id, file_type)
            return (True, "Uploaded", ws_id, file_id, file.filename, file_type)
        except Exception as e:
            self.logger.error(f"Upload error: {e}", exc_info=True)
            return (False, str(e), None, None, None, None)

    async def _store_file_in_postgres(self, filename: str, content_type: str, content: bytes) -> int:
        connection = None
        try:
            connection = PostgresConnection.get_connection()
            cursor = connection.cursor()
            query = "INSERT INTO storage_files (filename, content_type, file_content) VALUES (%s, %s, %s) RETURNING id;"
            cursor.execute(query, (filename, content_type, content))
            file_id = cursor.fetchone()['id']
            connection.commit()
            return int(file_id)
        finally:
            if connection: PostgresConnection.return_connection(connection)

    async def get_file_from_postgres(self, file_id: int) -> Optional[StreamingResponse]:
        connection = None
        try:
            connection = PostgresConnection.get_connection()
            cursor = connection.cursor()
            cursor.execute("SELECT filename, content_type, file_content FROM storage_files WHERE id = %s;", (file_id,))
            row = cursor.fetchone()
            if not row: return None
            return StreamingResponse(io.BytesIO(row['file_content']), media_type=row['content_type'], headers={"Content-Disposition": f"attachment; filename={row['filename']}"})
        finally:
            if connection: PostgresConnection.return_connection(connection)

    async def join_group(self, groupPublicId: str, userPublicId: str) -> bool:
        """Join a group."""
        self.logger.debug(f"join_group called with groupPublicId={groupPublicId}, userPublicId={userPublicId}")
        
        # Resolve public_ids to internal ids
        group_id = await self._resolve_group_id_from_public_id(groupPublicId)
        user_id = await self._resolve_user_id_from_public_id(userPublicId)
        
        if not group_id:
            self.logger.error(f"Failed to resolve group public_id: {groupPublicId}")
            return False
        if not user_id:
            self.logger.error(f"Failed to resolve user public_id: {userPublicId}")
            return False
        
        connection = None
        try:
            role = await self._get_or_create_member_role(group_id)
            connection = PostgresConnection.get_connection()
            cursor = connection.cursor()
            query = "INSERT INTO group_memberships (group_id, user_id, group_role_id) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING;"
            cursor.execute(query, (group_id, user_id, role['id']))
            connection.commit()
            success = cursor.rowcount > 0
            if success:
                self.logger.info(f"User {userPublicId} joined group {groupPublicId}")
            return success
        except Exception as e:
            if connection: connection.rollback()
            self.logger.error(f"Error joining group: {e}", exc_info=True)
            return False
        finally:
            if connection: PostgresConnection.return_connection(connection)

    async def leave_group(self, groupPublicId: str, userPublicId: str) -> bool:
        """Leave a group."""
        self.logger.debug(f"leave_group called with groupPublicId={groupPublicId}, userPublicId={userPublicId}")
        
        # Resolve public_ids to internal ids
        group_id = await self._resolve_group_id_from_public_id(groupPublicId)
        user_id = await self._resolve_user_id_from_public_id(userPublicId)
        
        if not group_id:
            self.logger.error(f"Failed to resolve group public_id: {groupPublicId}")
            return False
        if not user_id:
            self.logger.error(f"Failed to resolve user public_id: {userPublicId}")
            return False
        
        connection = None
        try:
            connection = PostgresConnection.get_connection()
            cursor = connection.cursor()
            cursor.execute("DELETE FROM group_memberships WHERE group_id = %s AND user_id = %s;", (group_id, user_id))
            connection.commit()
            success = cursor.rowcount > 0
            if success:
                self.logger.info(f"User {userPublicId} left group {groupPublicId}")
            return success
        except Exception as e:
            if connection: connection.rollback()
            self.logger.error(f"Error leaving group: {e}", exc_info=True)
            return False
        finally:
            if connection: PostgresConnection.return_connection(connection)

    async def get_groups_by_user_id(self, userPublicId: str) -> List[dict]:
        """Get all groups that a user is a member of."""
        self.logger.debug(f"get_groups_by_user_id called with userPublicId={userPublicId}")
        
        # Resolve public_id to internal id
        user_id = await self._resolve_user_id_from_public_id(userPublicId)
        if not user_id:
            self.logger.warning(f"User with public_id {userPublicId} not found")
            return []
        
        connection = None
        try:
            connection = PostgresConnection.get_connection()
            cursor = connection.cursor()
            # Use JOIN to get leader public_id and username in one query
            query = """
                SELECT 
                    g.id,
                    g.public_id,
                    g.name,
                    g.description,
                    g.leader_user_id,
                    g.location,
                    g.image,
                    g.study_plans,
                    g.meals,
                    g.meeting_consistency,
                    g.status,
                    g.meeting_days,
                    g.meeting_start_time,
                    g.meeting_end_time,
                    g.created_at,
                    g.updated_at,
                    u.id as leader_public_id,
                    COALESCE(
                        u.raw_user_meta_data->>'name',
                        u.raw_user_meta_data->>'full_name',
                        SPLIT_PART(u.email, '@', 1)
                    ) as leader_username
                FROM groups g
                JOIN group_memberships gm ON g.id = gm.group_id
                LEFT JOIN auth.users u ON g.leader_user_id::uuid = u.id
                WHERE gm.user_id = %s;
            """
            cursor.execute(query, (user_id,))
            results = cursor.fetchall()
            self.logger.debug(f"Found {len(results)} groups for user_id {user_id}")
            formatted_results = []
            for row in results:
                formatted_row = self._format_group_row(row)
                formatted_results.append(formatted_row)
            return formatted_results
        except Exception as e:
            self.logger.error(f"Error in get_groups_by_user_id: {e}", exc_info=True)
            return []
        finally:
            if connection: PostgresConnection.return_connection(connection)

    async def _create_worksheet_entry(self, groupId: int, title: str, content: str, file_id: int, file_type: str) -> int:
        connection = None
        try:
            connection = PostgresConnection.get_connection()
            cursor = connection.cursor()
            query = """INSERT INTO bible_worksheets (group_id, title, content, file_id, content_type)
                       VALUES (%s, %s, %s, %s, %s) RETURNING id;"""
            cursor.execute(query, (groupId, title, content, file_id, file_type))
            ws_id = cursor.fetchone()['id']
            connection.commit()
            return int(ws_id)
        finally:
            if connection: PostgresConnection.return_connection(connection)

    async def create_permission(self, action: str, description: str) -> Optional[int]:
        connection = None
        try:
            connection = PostgresConnection.get_connection()
            cursor = connection.cursor()
            cursor.execute("INSERT INTO permissions (action, description) VALUES (%s, %s) RETURNING id;", (action, description))
            p_id = cursor.fetchone()['id']
            connection.commit()
            return int(p_id)
        except Exception: return None
        finally:
            if connection: PostgresConnection.return_connection(connection)

    async def get_all_permissions(self) -> List[dict]:
        connection = None
        try:
            connection = PostgresConnection.get_connection()
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM permissions;")
            results = cursor.fetchall()
            for r in results: r['id'] = int(r['id'])
            return results
        finally:
            if connection: PostgresConnection.return_connection(connection)

    async def create_role(self, name: str, permissions: List[str]) -> Optional[int]:
        connection = None
        try:
            connection = PostgresConnection.get_connection()
            cursor = connection.cursor()
            cursor.execute("INSERT INTO roles (name, permissions) VALUES (%s, %s) RETURNING id;", (name, permissions))
            r_id = cursor.fetchone()['id']
            connection.commit()
            return int(r_id)
        finally:
            if connection: PostgresConnection.return_connection(connection)

    async def _get_or_create_member_role(self, groupId: int) -> dict:
        connection = None
        try:
            connection = PostgresConnection.get_connection()
            cursor = connection.cursor()
            cursor.execute("SELECT id FROM group_role_configs WHERE group_id = %s AND role_name = 'member';", (groupId,))
            row = cursor.fetchone()
            if row: return {'id': int(row['id'])}
            cursor.execute("INSERT INTO group_role_configs (group_id, role_name, permissions) VALUES (%s, 'member', '{}') RETURNING id;", (groupId,))
            new_id = cursor.fetchone()['id']
            connection.commit()
            return {'id': int(new_id)}
        finally:
            if connection: PostgresConnection.return_connection(connection)

    async def create_group_request(self, groupPublicId: str, userPublicId: str, message: str) -> Optional[int]:
        """Create a new group request."""
        self.logger.debug(f"create_group_request called with groupPublicId={groupPublicId}, userPublicId={userPublicId}")
        
        # Resolve public_ids to internal ids
        group_id = await self._resolve_group_id_from_public_id(groupPublicId)
        user_id = await self._resolve_user_id_from_public_id(userPublicId)
        
        if not group_id:
            self.logger.error(f"Failed to resolve group public_id: {groupPublicId}")
            return None
        if not user_id:
            self.logger.error(f"Failed to resolve user public_id: {userPublicId}")
            return None
        
        connection = None
        try:
            connection = PostgresConnection.get_connection()
            cursor = connection.cursor()
            cursor.execute("INSERT INTO group_requests (group_id, user_id, request_message) VALUES (%s, %s, %s) RETURNING id;", (group_id, user_id, message))
            req_id = cursor.fetchone()['id']
            connection.commit()
            self.logger.info(f"Group request created successfully with ID: {req_id}")
            return int(req_id)
        except Exception as e:
            if connection: connection.rollback()
            self.logger.error(f"Error creating group request: {e}", exc_info=True)
            return None
        finally:
            if connection: PostgresConnection.return_connection(connection)

    async def get_group_requests(self, groupPublicId: str) -> List[dict]:
        """Get all requests for a group."""
        self.logger.debug(f"get_group_requests called with groupPublicId={groupPublicId}")
        
        # Resolve public_id to internal id
        group_id = await self._resolve_group_id_from_public_id(groupPublicId)
        if not group_id:
            self.logger.warning(f"Group with public_id {groupPublicId} not found")
            return []
        
        connection = None
        try:
            connection = PostgresConnection.get_connection()
            cursor = connection.cursor()
            # Use JOINs to get group and user public_ids in one query
            query = """
                SELECT 
                    gr.id,
                    gr.group_id,
                    gr.user_id,
                    gr.request_message,
                    gr.created_at,
                    gr.status,
                    COALESCE(
                        u.raw_user_meta_data->>'name',
                        u.raw_user_meta_data->>'full_name',
                        SPLIT_PART(u.email, '@', 1)
                    ) as username,
                    g.public_id as group_public_id,
                    u.id as user_public_id
                FROM group_requests gr
                LEFT JOIN groups g ON gr.group_id = g.id
                LEFT JOIN auth.users u ON gr.user_id::uuid = u.id
                WHERE gr.group_id = %s
                ORDER BY gr.created_at DESC;
            """
            cursor.execute(query, (group_id,))
            results = cursor.fetchall()
            self.logger.debug(f"Found {len(results)} group requests for group_id {group_id}")
            formatted_results = []
            for r in results:
                formatted = {
                    'id': int(r['id']),
                    'groupId': str(r['group_public_id']) if r.get('group_public_id') else str(r['group_id']),
                    'userId': str(r['user_public_id']) if r.get('user_public_id') else str(r['user_id']),
                    'username': r.get('username'),
                    'createdAt': r['created_at'],
                    'requestMessage': r.get('request_message', ''),
                    'status': r.get('status', 'pending')
                }
                formatted_results.append(formatted)
            return formatted_results
        except Exception as e:
            self.logger.error(f"Error in get_group_requests: {e}", exc_info=True)
            return []
        finally:
            if connection: PostgresConnection.return_connection(connection)

    async def get_group_role_config_by_id(self, roleId: int) -> Optional[dict]:
        connection = None
        try:
            connection = PostgresConnection.get_connection()
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM group_role_configs WHERE id = %s;", (roleId,))
            row = cursor.fetchone()
            if row: row['id'] = int(row['id']); row['roleName'] = row['role_name']
            return row
        finally:
            if connection: PostgresConnection.return_connection(connection)

    async def get_group_role_config_by_name(self, groupPublicId: str, roleName: str) -> Optional[dict]:
        """Get a group role config by name."""
        self.logger.debug(f"get_group_role_config_by_name called with groupPublicId={groupPublicId}, roleName={roleName}")
        
        # Resolve public_id to internal id
        group_id = await self._resolve_group_id_from_public_id(groupPublicId)
        if not group_id:
            self.logger.warning(f"Group with public_id {groupPublicId} not found")
            return None
        
        connection = None
        try:
            connection = PostgresConnection.get_connection()
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM group_role_configs WHERE group_id = %s AND role_name = %s;", (group_id, roleName))
            row = cursor.fetchone()
            if row: row['id'] = int(row['id']); row['roleName'] = row['role_name']
            return row
        finally:
            if connection: PostgresConnection.return_connection(connection)

    async def create_group_role_config(self, groupPublicId: str, roleName: str, permissions: List[str]) -> Optional[int]:
        """Create a group role configuration."""
        self.logger.debug(f"create_group_role_config called with groupPublicId={groupPublicId}, roleName={roleName}")
        
        # Resolve public_id to internal id
        group_id = await self._resolve_group_id_from_public_id(groupPublicId)
        if not group_id:
            self.logger.error(f"Failed to resolve group public_id: {groupPublicId}")
            return None
        
        connection = None
        try:
            connection = PostgresConnection.get_connection()
            cursor = connection.cursor()
            cursor.execute("INSERT INTO group_role_configs (group_id, role_name, permissions) VALUES (%s, %s, %s) RETURNING id;", (group_id, roleName, permissions))
            rc_id = cursor.fetchone()['id']
            connection.commit()
            self.logger.info(f"Group role config created successfully with ID: {rc_id}")
            return int(rc_id)
        except Exception as e:
            if connection: connection.rollback()
            self.logger.error(f"Error creating group role config: {e}", exc_info=True)
            return None
        finally:
            if connection: PostgresConnection.return_connection(connection)

    async def get_group_role_configs(self, groupPublicId: str) -> List[dict]:
        """Get all role configurations for a group."""
        self.logger.debug(f"get_group_role_configs called with groupPublicId={groupPublicId}")
        
        # Resolve public_id to internal id
        group_id = await self._resolve_group_id_from_public_id(groupPublicId)
        if not group_id:
            self.logger.warning(f"Group with public_id {groupPublicId} not found")
            return []
        
        connection = None
        try:
            connection = PostgresConnection.get_connection()
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM group_role_configs WHERE group_id = %s;", (group_id,))
            results = cursor.fetchall()
            for r in results: r['id'] = int(r['id']); r['roleName'] = r['role_name']
            return results
        finally:
            if connection: PostgresConnection.return_connection(connection)

    async def update_group_role_config(self, groupPublicId: str, roleName: str, permissions: List[str]) -> bool:
        """Update a group role configuration."""
        self.logger.debug(f"update_group_role_config called with groupPublicId={groupPublicId}, roleName={roleName}")
        
        # Resolve public_id to internal id
        group_id = await self._resolve_group_id_from_public_id(groupPublicId)
        if not group_id:
            self.logger.error(f"Failed to resolve group public_id: {groupPublicId}")
            return False
        
        connection = None
        try:
            connection = PostgresConnection.get_connection()
            cursor = connection.cursor()
            cursor.execute("UPDATE group_role_configs SET permissions = %s, updated_at = %s WHERE group_id = %s AND role_name = %s;", (permissions, datetime.utcnow(), group_id, roleName))
            connection.commit()
            success = cursor.rowcount > 0
            if success:
                self.logger.info(f"Group role config updated successfully")
            return success
        except Exception as e:
            if connection: connection.rollback()
            self.logger.error(f"Error updating group role config: {e}", exc_info=True)
            return False
        finally:
            if connection: PostgresConnection.return_connection(connection)

    async def delete_group_role_config(self, groupPublicId: str, roleName: str) -> bool:
        """Delete a group role configuration."""
        self.logger.debug(f"delete_group_role_config called with groupPublicId={groupPublicId}, roleName={roleName}")
        
        # Resolve public_id to internal id
        group_id = await self._resolve_group_id_from_public_id(groupPublicId)
        if not group_id:
            self.logger.error(f"Failed to resolve group public_id: {groupPublicId}")
            return False
        
        connection = None
        try:
            connection = PostgresConnection.get_connection()
            cursor = connection.cursor()
            cursor.execute("DELETE FROM group_role_configs WHERE group_id = %s AND role_name = %s;", (group_id, roleName))
            connection.commit()
            success = cursor.rowcount > 0
            if success:
                self.logger.info(f"Group role config deleted successfully")
            return success
        except Exception as e:
            if connection: connection.rollback()
            self.logger.error(f"Error deleting group role config: {e}", exc_info=True)
            return False
        finally:
            if connection: PostgresConnection.return_connection(connection)

    async def get_file_from_gridfs(self, file_id: int) -> Optional[StreamingResponse]:
        return await self.get_file_from_postgres(file_id)

    async def create_worksheet_text(self, groupPublicId: str, title: str, content: str) -> str:
        """Create a worksheet with HTML/text content."""
        ws_id = await self.create_worksheet(groupPublicId, title, content)
        return str(ws_id) if ws_id else ""
