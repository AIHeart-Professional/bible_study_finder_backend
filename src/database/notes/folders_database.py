"""Folders database - Data access layer for users_folders using Supabase HTTP API."""
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID

from src.utils.logger import get_logger
from src.utils.supabase_client import SupabaseClient


class FoldersDatabase:
    """Database layer for user folders (users_folders table)."""

    TABLE = "users_folders"

    def __init__(self):
        """Initialize the database connection."""
        self.logger = get_logger(__name__)
        self.client = SupabaseClient.get_instance()
        self.logger.info("FoldersDatabase initialized successfully (using Supabase HTTP API)")

    def _validate_uuid(self, value: str) -> Optional[str]:
        """Validate and return UUID string."""
        try:
            UUID(value)
            return value
        except (ValueError, TypeError):
            self.logger.error(f"Invalid UUID format: {value}")
            return None

    async def list_folders(self, userPublicId: str) -> List[Dict[str, Any]]:
        """List all folders for a user, ordered by name."""
        self.logger.debug(f"list_folders called for userPublicId={userPublicId}")
        user_uuid = self._validate_uuid(userPublicId)
        if not user_uuid:
            return []

        try:
            rows = await self.client.select(
                table=self.TABLE,
                columns="id,user_id,name,parent_id,created_at,updated_at",
                filters={"user_id": user_uuid},
                order="name.asc",
            )
            self.logger.info(f"list_folders returned {len(rows)} folders for user {userPublicId}")
            return rows
        except Exception as e:
            self.logger.error(f"Error in list_folders: {e}", exc_info=True)
            raise

    async def get_folder_by_id(self, folderId: str, userPublicId: str) -> Optional[Dict[str, Any]]:
        """Get a single folder by id and user."""
        self.logger.debug(f"get_folder_by_id called folderId={folderId}, userPublicId={userPublicId}")
        user_uuid = self._validate_uuid(userPublicId)
        if not user_uuid or not self._validate_uuid(folderId):
            return None

        try:
            rows = await self.client.select(
                table=self.TABLE,
                columns="id,user_id,name,parent_id,created_at,updated_at",
                filters={"id": folderId, "user_id": user_uuid},
            )
            if not rows:
                self.logger.warning(f"Folder not found: id={folderId}, userPublicId={userPublicId}")
                return None
            return rows[0]
        except Exception as e:
            self.logger.error(f"Error in get_folder_by_id: {e}", exc_info=True)
            raise

    async def get_folders_by_ids(self, folder_ids: List[str]) -> List[Dict[str, Any]]:
        """Get multiple folders by ids (for attaching to notes)."""
        if not folder_ids:
            return []
        valid_ids = [f for f in folder_ids if self._validate_uuid(f)]
        if not valid_ids:
            return []

        try:
            rows = await self.client.select(
                table=self.TABLE,
                columns="id,user_id,name,parent_id,created_at,updated_at",
                filters={"id": valid_ids},
            )
            return rows
        except Exception as e:
            self.logger.error(f"Error in get_folders_by_ids: {e}", exc_info=True)
            raise

    async def create_folder(
        self,
        userPublicId: str,
        name: str,
        parentId: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Create a new folder."""
        self.logger.debug(f"create_folder called for userPublicId={userPublicId}, name={name}")
        user_uuid = self._validate_uuid(userPublicId)
        if not user_uuid:
            return None

        data = {
            "user_id": user_uuid,
            "name": name,
        }
        if parentId:
            parent_uuid = self._validate_uuid(parentId)
            if parent_uuid:
                data["parent_id"] = parent_uuid
        # Omit parent_id when null so PostgREST uses column default and avoids 409

        try:
            row = await self.client.insert(table=self.TABLE, data=data, return_data=True)
            self.logger.info(f"create_folder created folder id={row.get('id')} for user {userPublicId}")
            return row
        except Exception as e:
            self.logger.error(f"Error in create_folder: {e}", exc_info=True)
            raise

    async def update_folder(
        self,
        folderId: str,
        userPublicId: str,
        name: Optional[str] = None,
        parentId: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Update an existing folder. Only non-None fields are updated."""
        self.logger.debug(f"update_folder called folderId={folderId}, userPublicId={userPublicId}")
        user_uuid = self._validate_uuid(userPublicId)
        if not user_uuid or not self._validate_uuid(folderId):
            return None

        data = {"updated_at": datetime.utcnow().isoformat() + "Z"}
        if name is not None:
            data["name"] = name
        if parentId is not None:
            data["parent_id"] = self._validate_uuid(parentId)

        try:
            rows = await self.client.update(
                table=self.TABLE,
                data=data,
                filters={"id": folderId, "user_id": user_uuid},
                return_data=True,
            )
            if not rows:
                self.logger.warning(f"Folder not found for update: id={folderId}, userPublicId={userPublicId}")
                return None
            self.logger.info(f"update_folder updated folder id={folderId}")
            return rows[0]
        except Exception as e:
            self.logger.error(f"Error in update_folder: {e}", exc_info=True)
            raise

    async def delete_folder(self, folderId: str, userPublicId: str) -> bool:
        """Delete a folder (notes in it will have folder_id set to null via ON DELETE SET NULL)."""
        self.logger.debug(f"delete_folder called folderId={folderId}, userPublicId={userPublicId}")
        user_uuid = self._validate_uuid(userPublicId)
        if not user_uuid or not self._validate_uuid(folderId):
            return False

        try:
            await self.client.delete(
                table=self.TABLE,
                filters={"id": folderId, "user_id": user_uuid},
                return_data=False,
            )
            self.logger.info(f"delete_folder deleted folder id={folderId}")
            return True
        except Exception as e:
            self.logger.error(f"Error in delete_folder: {e}", exc_info=True)
            raise
