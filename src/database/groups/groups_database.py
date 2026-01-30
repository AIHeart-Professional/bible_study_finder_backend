"""Groups database - Data access layer using Supabase HTTP API."""
import io
import json
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
from fastapi import UploadFile
from fastapi.responses import StreamingResponse
from src.utils.logger import get_logger
from src.utils.supabase_client import SupabaseClient
from src.utils.text_extractor import TextExtractor


class GroupsDatabase:
    """Database layer for group operations using Supabase HTTP API."""
    
    def __init__(self):
        """Initialize the database connection."""
        self.logger = get_logger(__name__)
        self.client = SupabaseClient.get_instance()
        self.logger.info("GroupsDatabase initialized successfully (using Supabase HTTP API)")

    async def _resolve_user_id_from_public_id(self, public_id: str) -> Optional[str]:
        """Resolve user's public_id (UUID) - validates and returns it."""
        self.logger.debug(f"_resolve_user_id_from_public_id called with public_id={public_id}")
        
        try:
            UUID(public_id)
            return public_id
        except ValueError:
            self.logger.error(f"Invalid UUID format: {public_id}")
            return None

    async def _resolve_group_id_from_public_id(self, public_id: str) -> Optional[int]:
        """Resolve group's public_id (UUID) to internal id (BIGINT)."""
        self.logger.debug(f"_resolve_group_id_from_public_id called with public_id={public_id}")
        
        try:
            UUID(public_id)
        except ValueError:
            self.logger.error(f"Invalid UUID format: {public_id}")
            return None
        
        try:
            result = await self.client.rpc("resolve_group_id", {"p_public_id": public_id})
            
            if result is not None:
                self.logger.debug(f"Resolved group public_id {public_id} to internal id {result}")
                return int(result)
            
            self.logger.warning(f"Group with public_id {public_id} not found")
            return None
            
        except Exception as e:
            self.logger.error(f"Error resolving group_id from public_id: {e}", exc_info=True)
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
        """Create a new group in the database."""
        self.logger.debug(f"create_group called with name={name}, leaderPublicId={leaderPublicId}")
        
        leader_user_id = await self._resolve_user_id_from_public_id(leaderPublicId)
        if not leader_user_id:
            self.logger.error(f"Failed to resolve leader public_id: {leaderPublicId}")
            return None
        
        try:
            result = await self.client.rpc("create_group_rpc", {
                "p_name": name,
                "p_description": description,
                "p_leader_user_id": leader_user_id,
                "p_location": location,
                "p_meeting_start_time": meetingStartTime.isoformat() if meetingStartTime else None,
                "p_meeting_end_time": meetingEndTime.isoformat() if meetingEndTime else None,
                "p_gender_focus": genderFocus,
                "p_meeting_days": meetingDays,
                "p_demographic": demographic,
                "p_group_type": groupType,
                "p_meeting_consistency": meetingConsistency,
                "p_meeting_format": meetingFormat,
                "p_status": status
            })
            
            if result:
                self.logger.info(f"Group created successfully with public_id: {result}")
                return str(result)
            return None
            
        except Exception as e:
            self.logger.error(f"Error creating group: {e}", exc_info=True)
            return None

    async def initialize_group(self, groupPublicId: str) -> bool:
        """Initialize a group with empty study plans and meals."""
        self.logger.debug(f"initialize_group called with groupPublicId={groupPublicId}")
        
        group_id = await self._resolve_group_id_from_public_id(groupPublicId)
        if not group_id:
            return False
        
        try:
            await self.client.update(
                "groups",
                {"study_plans": [], "meals": [], "updated_at": datetime.utcnow().isoformat()},
                {"id": group_id}
            )
            return True
        except Exception as e:
            self.logger.error(f"Error initializing group: {e}", exc_info=True)
            return False

    async def get_all_groups(self) -> List[dict]:
        """Get all groups from the database."""
        self.logger.debug("get_all_groups called")
        
        try:
            results = await self.client.rpc("get_all_groups_with_leader")
            
            formatted_results = []
            for row in results:
                formatted_row = self._format_group_row(row)
                formatted_results.append(formatted_row)
            
            self.logger.debug(f"Found {len(formatted_results)} groups")
            return formatted_results
            
        except Exception as e:
            self.logger.error(f"Error in get_all_groups: {e}", exc_info=True)
            return []

    def _format_group_row(self, row: dict) -> dict:
        """Format group database row to dictionary."""
        row['id'] = int(row['id']) if row.get('id') else None
        if row.get('public_id'):
            row['public_id'] = str(row['public_id'])
        if row.get('leader_public_id'):
            row['leaderUserId'] = str(row['leader_public_id'])
        elif row.get('leader_user_id'):
            row['leaderUserId'] = str(row['leader_user_id'])
        row['leaderUsername'] = row.get('leader_username')
        row['createdAt'] = row.get('created_at')
        row['updatedAt'] = row.get('updated_at')
        row['studyPlans'] = row.get('study_plans', []) or []
        row['meals'] = row.get('meals', []) or []
        row['meetingConsistency'] = row.get('meeting_consistency')
        row['status'] = row.get('status')
        row['meetingDays'] = self._parse_meeting_days(row.get('meeting_days'))
        row['meetingStartTime'] = row.get('meeting_start_time')
        row['meetingEndTime'] = row.get('meeting_end_time')
        row['genderFocus'] = row.get('gender_focus')
        row['demographic'] = row.get('demographic')
        row['groupType'] = row.get('group_type')
        row['meetingFormat'] = row.get('meeting_format')
        return row

    def _parse_meeting_days(self, meeting_days) -> List[str]:
        """Parse meeting_days field to list."""
        if meeting_days is None:
            return []
        if isinstance(meeting_days, list):
            return meeting_days
        if isinstance(meeting_days, str):
            try:
                parsed = json.loads(meeting_days)
                return parsed if isinstance(parsed, list) else [parsed] if parsed else []
            except (json.JSONDecodeError, TypeError):
                return [meeting_days] if meeting_days else []
        try:
            return list(meeting_days) if meeting_days else []
        except (TypeError, ValueError):
            return []

    async def get_group_by_public_id(self, public_id: str) -> Optional[dict]:
        """Get group by public_id (UUID)."""
        self.logger.debug(f"get_group_by_public_id called with public_id={public_id}")
        
        group_id = await self._resolve_group_id_from_public_id(public_id)
        if not group_id:
            return None
        
        return await self.get_group_by_id(group_id)

    async def get_group_by_id(self, groupId: int) -> Optional[dict]:
        """Get group by internal ID."""
        self.logger.debug(f"get_group_by_id called with groupId={groupId}")
        
        try:
            results = await self.client.rpc("get_group_by_id_with_leader", {"p_group_id": groupId})
            
            if results and len(results) > 0:
                return self._format_group_row(results[0])
            return None
            
        except Exception as e:
            self.logger.error(f"Error in get_group_by_id: {e}", exc_info=True)
            return None

    async def get_group_members(self, groupPublicId: str) -> List[dict]:
        """Get all members of a group with role information."""
        self.logger.debug(f"get_group_members called with groupPublicId={groupPublicId}")
        
        group_id = await self._resolve_group_id_from_public_id(groupPublicId)
        if not group_id:
            return []
        
        try:
            results = await self.client.rpc("get_group_members_with_info", {"p_group_id": group_id})
            
            formatted_results = []
            for row in results:
                formatted_row = self._format_membership_row(row)
                formatted_results.append(formatted_row)
            
            self.logger.debug(f"Found {len(formatted_results)} members")
            return formatted_results
            
        except Exception as e:
            self.logger.error(f"Error in get_group_members: {e}", exc_info=True)
            return []

    def _format_membership_row(self, row: dict) -> dict:
        """Format membership row."""
        return {
            'id': int(row['id']),
            'groupId': int(row['group_id']),
            'userId': str(row.get('user_public_id') or row.get('user_id')),
            'username': row.get('username', ''),
            'email': row.get('email', ''),
            'portraitUrl': None,
            'joinedAt': row.get('joined_at'),
            'role': row.get('role', 'member') or 'member',
            'permissions': row.get('permissions', []) or []
        }

    async def get_group_meals(self, groupPublicId: str) -> List[dict]:
        """Get all meals for a group (from JSONB field)."""
        self.logger.debug(f"get_group_meals called with groupPublicId={groupPublicId}")
        
        group_id = await self._resolve_group_id_from_public_id(groupPublicId)
        if not group_id:
            return []
        
        try:
            results = await self.client.select("groups", "meals", {"id": group_id})
            
            if results and len(results) > 0:
                meals = results[0].get('meals', [])
                return meals if isinstance(meals, list) else []
            return []
            
        except Exception as e:
            self.logger.error(f"Error in get_group_meals: {e}", exc_info=True)
            return []
    
    async def get_group_study_plans(self, groupPublicId: str) -> List[dict]:
        """Get all study plans for a group (from JSONB field)."""
        self.logger.debug(f"get_group_study_plans called with groupPublicId={groupPublicId}")
        
        group_id = await self._resolve_group_id_from_public_id(groupPublicId)
        if not group_id:
            return []
        
        try:
            results = await self.client.select("groups", "study_plans", {"id": group_id})
            
            if results and len(results) > 0:
                plans = results[0].get('study_plans', [])
                return plans if isinstance(plans, list) else []
            return []
            
        except Exception as e:
            self.logger.error(f"Error in get_group_study_plans: {e}", exc_info=True)
            return []

    async def get_group_chats(self, groupPublicId: str) -> List[dict]:
        """Get all chat messages for a group."""
        self.logger.debug(f"get_group_chats called with groupPublicId={groupPublicId}")
        
        group_id = await self._resolve_group_id_from_public_id(groupPublicId)
        if not group_id:
            return []
        
        try:
            results = await self.client.rpc("get_group_chats_with_info", {"p_group_id": group_id})
            
            formatted_results = []
            for r in results:
                formatted = {
                    'id': int(r['id']),
                    'groupId': int(r['group_id']),
                    'userId': str(r.get('user_public_id') or r.get('user_id')),
                    'username': r.get('username', ''),
                    'message': r.get('message', ''),
                    'sentAt': r.get('sent_at')
                }
                formatted_results.append(formatted)
            
            self.logger.debug(f"Found {len(formatted_results)} chat messages")
            return formatted_results
            
        except Exception as e:
            self.logger.error(f"Error in get_group_chats: {e}", exc_info=True)
            return []

    async def create_group_chat(self, groupPublicId: str, userPublicId: str, message: str) -> Optional[int]:
        """Create a new group chat message."""
        self.logger.debug(f"create_group_chat called with groupPublicId={groupPublicId}, userPublicId={userPublicId}")
        
        group_id = await self._resolve_group_id_from_public_id(groupPublicId)
        user_id = await self._resolve_user_id_from_public_id(userPublicId)
        
        if not group_id or not user_id:
            return None
        
        try:
            result = await self.client.insert("group_chats", {
                "group_id": group_id,
                "user_id": user_id,
                "message": message
            })
            
            if result:
                chat_id = int(result['id'])
                self.logger.info(f"Group chat created with ID: {chat_id}")
                return chat_id
            return None
            
        except Exception as e:
            self.logger.error(f"Error creating group chat: {e}", exc_info=True)
            return None

    async def create_worksheet(self, groupPublicId: str, title: str, content: str) -> Optional[int]:
        """Create a new Bible worksheet."""
        self.logger.debug(f"create_worksheet called with groupPublicId={groupPublicId}")
        
        group_id = await self._resolve_group_id_from_public_id(groupPublicId)
        if not group_id:
            return None
        
        try:
            result = await self.client.insert("bible_worksheets", {
                "group_id": group_id,
                "title": title,
                "content": content
            })
            
            if result:
                ws_id = int(result['id'])
                self.logger.info(f"Worksheet created with ID: {ws_id}")
                return ws_id
            return None
            
        except Exception as e:
            self.logger.error(f"Error creating worksheet: {e}", exc_info=True)
            return None

    async def get_group_worksheets(self, groupPublicId: str) -> List[dict]:
        """Get all worksheets for a group."""
        self.logger.debug(f"get_group_worksheets called with groupPublicId={groupPublicId}")
        
        group_id = await self._resolve_group_id_from_public_id(groupPublicId)
        if not group_id:
            return []
        
        try:
            results = await self.client.select(
                "bible_worksheets", 
                "*", 
                {"group_id": group_id},
                order="created_at.desc"
            )
            
            for r in results:
                r['id'] = int(r['id'])
                r['groupId'] = int(r['group_id'])
                r['createdAt'] = r.get('created_at')
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error in get_group_worksheets: {e}", exc_info=True)
            return []

    async def upload_worksheet_file(self, groupPublicId: str, title: str, file: UploadFile, file_type: str) -> tuple:
        """Upload a worksheet file."""
        self.logger.debug(f"upload_worksheet_file called with groupPublicId={groupPublicId}")
        
        group_id = await self._resolve_group_id_from_public_id(groupPublicId)
        if not group_id:
            return (False, f"Group not found", None, None, None, None)
        
        try:
            content = await file.read()
            file_id = await self._store_file(file.filename, file.content_type, content)
            extracted = await TextExtractor.extract_text(content, file_type)
            ws_id = await self._create_worksheet_entry(group_id, title, extracted, file_id, file_type)
            return (True, "Uploaded", ws_id, file_id, file.filename, file_type)
        except Exception as e:
            self.logger.error(f"Upload error: {e}", exc_info=True)
            return (False, str(e), None, None, None, None)

    async def _store_file(self, filename: str, content_type: str, content: bytes) -> int:
        """Store file in database."""
        try:
            # Note: Storing binary files via REST API requires base64 encoding
            import base64
            encoded_content = base64.b64encode(content).decode('utf-8')
            
            result = await self.client.insert("storage_files", {
                "filename": filename,
                "content_type": content_type,
                "file_content": encoded_content
            })
            
            return int(result['id']) if result else None
            
        except Exception as e:
            self.logger.error(f"Error storing file: {e}", exc_info=True)
            raise

    async def get_file_from_postgres(self, file_id: int) -> Optional[StreamingResponse]:
        """Get file from database."""
        try:
            results = await self.client.select(
                "storage_files",
                "filename,content_type,file_content",
                {"id": file_id}
            )
            
            if not results:
                return None
            
            row = results[0]
            import base64
            content = base64.b64decode(row['file_content'])
            
            return StreamingResponse(
                io.BytesIO(content),
                media_type=row['content_type'],
                headers={"Content-Disposition": f"attachment; filename={row['filename']}"}
            )
            
        except Exception as e:
            self.logger.error(f"Error getting file: {e}", exc_info=True)
            return None

    async def join_group(self, groupPublicId: str, userPublicId: str) -> bool:
        """Join a group."""
        self.logger.debug(f"join_group called with groupPublicId={groupPublicId}, userPublicId={userPublicId}")
        
        group_id = await self._resolve_group_id_from_public_id(groupPublicId)
        user_id = await self._resolve_user_id_from_public_id(userPublicId)
        
        if not group_id or not user_id:
            return False
        
        try:
            role_id = await self.client.rpc("get_or_create_member_role", {"p_group_id": group_id})
            
            await self.client.insert("group_memberships", {
                "group_id": group_id,
                "user_id": user_id,
                "group_role_id": role_id
            })
            
            self.logger.info(f"User {userPublicId} joined group {groupPublicId}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error joining group: {e}", exc_info=True)
            return False

    async def leave_group(self, groupPublicId: str, userPublicId: str) -> bool:
        """Leave a group."""
        self.logger.debug(f"leave_group called with groupPublicId={groupPublicId}, userPublicId={userPublicId}")
        
        group_id = await self._resolve_group_id_from_public_id(groupPublicId)
        user_id = await self._resolve_user_id_from_public_id(userPublicId)
        
        if not group_id or not user_id:
            return False
        
        try:
            await self.client.delete("group_memberships", {
                "group_id": group_id,
                "user_id": user_id
            })
            
            self.logger.info(f"User {userPublicId} left group {groupPublicId}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error leaving group: {e}", exc_info=True)
            return False

    async def get_groups_by_user_id(self, userPublicId: str) -> List[dict]:
        """Get all groups that a user is a member of."""
        self.logger.debug(f"get_groups_by_user_id called with userPublicId={userPublicId}")
        
        user_id = await self._resolve_user_id_from_public_id(userPublicId)
        if not user_id:
            return []
        
        try:
            results = await self.client.rpc("get_groups_by_user_id_with_leader", {"p_user_id": user_id})
            
            formatted_results = []
            for row in results:
                formatted_row = self._format_group_row(row)
                formatted_results.append(formatted_row)
            
            self.logger.debug(f"Found {len(formatted_results)} groups for user")
            return formatted_results
            
        except Exception as e:
            self.logger.error(f"Error in get_groups_by_user_id: {e}", exc_info=True)
            return []

    async def _create_worksheet_entry(self, groupId: int, title: str, content: str, file_id: int, file_type: str) -> int:
        """Create worksheet database entry."""
        try:
            result = await self.client.insert("bible_worksheets", {
                "group_id": groupId,
                "title": title,
                "content": content,
                "file_id": file_id,
                "content_type": file_type
            })
            
            return int(result['id']) if result else None
            
        except Exception as e:
            self.logger.error(f"Error creating worksheet entry: {e}", exc_info=True)
            raise

    async def create_permission(self, action: str, description: str) -> Optional[int]:
        """Create a new permission."""
        try:
            result = await self.client.insert("permissions", {
                "action": action,
                "description": description
            })
            return int(result['id']) if result else None
        except Exception:
            return None

    async def get_all_permissions(self) -> List[dict]:
        """Get all permissions."""
        try:
            results = await self.client.select("permissions", "*")
            for r in results:
                r['id'] = int(r['id'])
            return results
        except Exception:
            return []

    async def create_role(self, name: str, permissions: List[str]) -> Optional[int]:
        """Create a new role."""
        try:
            result = await self.client.insert("roles", {
                "name": name,
                "permissions": permissions
            })
            return int(result['id']) if result else None
        except Exception:
            return None

    async def create_group_request(self, groupPublicId: str, userPublicId: str, message: str) -> Optional[int]:
        """Create a new group request."""
        self.logger.debug(f"create_group_request called with groupPublicId={groupPublicId}, userPublicId={userPublicId}")
        
        group_id = await self._resolve_group_id_from_public_id(groupPublicId)
        user_id = await self._resolve_user_id_from_public_id(userPublicId)
        
        if not group_id or not user_id:
            return None
        
        try:
            result = await self.client.insert("group_requests", {
                "group_id": group_id,
                "user_id": user_id,
                "request_message": message
            })
            
            if result:
                req_id = int(result['id'])
                self.logger.info(f"Group request created with ID: {req_id}")
                return req_id
            return None
            
        except Exception as e:
            self.logger.error(f"Error creating group request: {e}", exc_info=True)
            return None

    async def get_group_requests(self, groupPublicId: str) -> List[dict]:
        """Get all requests for a group."""
        self.logger.debug(f"get_group_requests called with groupPublicId={groupPublicId}")
        
        group_id = await self._resolve_group_id_from_public_id(groupPublicId)
        if not group_id:
            return []
        
        try:
            results = await self.client.rpc("get_group_requests_with_info", {"p_group_id": group_id})
            
            formatted_results = []
            for r in results:
                formatted = {
                    'id': int(r['id']),
                    'groupId': str(r.get('group_public_id') or r.get('group_id')),
                    'userId': str(r.get('user_public_id') or r.get('user_id')),
                    'username': r.get('username'),
                    'createdAt': r.get('created_at'),
                    'requestMessage': r.get('request_message', ''),
                    'status': r.get('status', 'pending')
                }
                formatted_results.append(formatted)
            
            self.logger.debug(f"Found {len(formatted_results)} group requests")
            return formatted_results
            
        except Exception as e:
            self.logger.error(f"Error in get_group_requests: {e}", exc_info=True)
            return []

    async def get_group_role_config_by_id(self, roleId: int) -> Optional[dict]:
        """Get group role config by ID."""
        try:
            results = await self.client.select("group_role_configs", "*", {"id": roleId})
            
            if results and len(results) > 0:
                row = results[0]
                row['id'] = int(row['id'])
                row['roleName'] = row.get('role_name')
                return row
            return None
            
        except Exception:
            return None

    async def get_group_role_config_by_name(self, groupPublicId: str, roleName: str) -> Optional[dict]:
        """Get a group role config by name."""
        self.logger.debug(f"get_group_role_config_by_name called with groupPublicId={groupPublicId}, roleName={roleName}")
        
        group_id = await self._resolve_group_id_from_public_id(groupPublicId)
        if not group_id:
            return None
        
        try:
            results = await self.client.select("group_role_configs", "*", {
                "group_id": group_id,
                "role_name": roleName
            })
            
            if results and len(results) > 0:
                row = results[0]
                row['id'] = int(row['id'])
                row['roleName'] = row.get('role_name')
                return row
            return None
            
        except Exception:
            return None

    async def create_group_role_config(self, groupPublicId: str, roleName: str, permissions: List[str]) -> Optional[int]:
        """Create a group role configuration."""
        self.logger.debug(f"create_group_role_config called with groupPublicId={groupPublicId}, roleName={roleName}")
        
        group_id = await self._resolve_group_id_from_public_id(groupPublicId)
        if not group_id:
            return None
        
        try:
            result = await self.client.insert("group_role_configs", {
                "group_id": group_id,
                "role_name": roleName,
                "permissions": permissions
            })
            
            if result:
                rc_id = int(result['id'])
                self.logger.info(f"Group role config created with ID: {rc_id}")
                return rc_id
            return None
            
        except Exception as e:
            self.logger.error(f"Error creating group role config: {e}", exc_info=True)
            return None

    async def get_group_role_configs(self, groupPublicId: str) -> List[dict]:
        """Get all role configurations for a group."""
        self.logger.debug(f"get_group_role_configs called with groupPublicId={groupPublicId}")
        
        group_id = await self._resolve_group_id_from_public_id(groupPublicId)
        if not group_id:
            return []
        
        try:
            results = await self.client.select("group_role_configs", "*", {"group_id": group_id})
            
            for r in results:
                r['id'] = int(r['id'])
                r['roleName'] = r.get('role_name')
            
            return results
            
        except Exception:
            return []

    async def update_group_role_config(self, groupPublicId: str, roleName: str, permissions: List[str]) -> bool:
        """Update a group role configuration."""
        self.logger.debug(f"update_group_role_config called with groupPublicId={groupPublicId}, roleName={roleName}")
        
        group_id = await self._resolve_group_id_from_public_id(groupPublicId)
        if not group_id:
            return False
        
        try:
            await self.client.update(
                "group_role_configs",
                {"permissions": permissions, "updated_at": datetime.utcnow().isoformat()},
                {"group_id": group_id, "role_name": roleName}
            )
            
            self.logger.info(f"Group role config updated successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating group role config: {e}", exc_info=True)
            return False

    async def delete_group_role_config(self, groupPublicId: str, roleName: str) -> bool:
        """Delete a group role configuration."""
        self.logger.debug(f"delete_group_role_config called with groupPublicId={groupPublicId}, roleName={roleName}")
        
        group_id = await self._resolve_group_id_from_public_id(groupPublicId)
        if not group_id:
            return False
        
        try:
            await self.client.delete("group_role_configs", {
                "group_id": group_id,
                "role_name": roleName
            })
            
            self.logger.info(f"Group role config deleted successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error deleting group role config: {e}", exc_info=True)
            return False

    async def get_file_from_gridfs(self, file_id: int) -> Optional[StreamingResponse]:
        """Legacy method - redirects to get_file_from_postgres."""
        return await self.get_file_from_postgres(file_id)

    async def create_worksheet_text(self, groupPublicId: str, title: str, content: str) -> str:
        """Create a worksheet with HTML/text content."""
        ws_id = await self.create_worksheet(groupPublicId, title, content)
        return str(ws_id) if ws_id else ""
