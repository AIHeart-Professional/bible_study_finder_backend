"""Folders service - Application logic layer for user folders."""
from typing import List, Optional, Tuple

import httpx
from src.utils.logger import get_logger
from src.database.notes.folders_database import FoldersDatabase


class FoldersService:
    """Service for user folders CRUD."""

    def __init__(self):
        """Initialize the service and database."""
        self.logger = get_logger(__name__)
        self.folders_database = FoldersDatabase()
        self.logger.info("FoldersService initialized successfully")

    def _parse_datetime(self, dt_value) -> Optional[str]:
        """Return ISO string for API."""
        if dt_value is None:
            return None
        if hasattr(dt_value, "isoformat"):
            return dt_value.isoformat()
        if isinstance(dt_value, str):
            return dt_value
        return str(dt_value)

    def _row_to_folder(self, row: dict) -> dict:
        """Map DB row to folder dict for response."""
        return {
            "id": str(row["id"]),
            "userPublicId": str(row["user_id"]),
            "name": row.get("name", ""),
            "parentId": str(row["parent_id"]) if row.get("parent_id") else None,
            "createdAt": self._parse_datetime(row.get("created_at")),
            "updatedAt": self._parse_datetime(row.get("updated_at")),
        }

    async def list_folders(self, userPublicId: str) -> Tuple[bool, str, List[dict]]:
        """List all folders for a user."""
        self.logger.debug(f"list_folders called userPublicId={userPublicId}")
        try:
            rows = await self.folders_database.list_folders(userPublicId)
            folders = [self._row_to_folder(r) for r in rows]
            self.logger.info(f"list_folders returned {len(folders)} folders")
            return True, "Folders retrieved successfully", folders
        except Exception as e:
            self.logger.error(f"Error in list_folders: {e}", exc_info=True)
            return False, f"Error retrieving folders: {str(e)}", []

    async def get_folder(self, folderId: str, userPublicId: str) -> Tuple[bool, str, Optional[dict]]:
        """Get a single folder by id."""
        self.logger.debug(f"get_folder called folderId={folderId}, userPublicId={userPublicId}")
        try:
            row = await self.folders_database.get_folder_by_id(folderId, userPublicId)
            if not row:
                return False, "Folder not found", None
            return True, "Folder retrieved successfully", self._row_to_folder(row)
        except Exception as e:
            self.logger.error(f"Error in get_folder: {e}", exc_info=True)
            return False, f"Error retrieving folder: {str(e)}", None

    async def create_folder(
        self,
        userPublicId: str,
        name: str,
        parentId: Optional[str] = None,
    ) -> Tuple[bool, str, Optional[dict]]:
        """Create a new folder."""
        self.logger.debug(f"create_folder called userPublicId={userPublicId}, name={name}")
        try:
            row = await self.folders_database.create_folder(
                userPublicId=userPublicId,
                name=name,
                parentId=parentId,
            )
            if not row:
                return False, "Failed to create folder", None
            self.logger.info(f"create_folder created folder id={row.get('id')}")
            return True, "Folder created successfully", self._row_to_folder(row)
        except httpx.HTTPStatusError as e:
            self.logger.error(f"Error in create_folder: {e.response.status_code} - {e.response.text}", exc_info=True)
            if e.response.status_code == 409:
                try:
                    body = e.response.json()
                    detail = body.get("message") or body.get("details") or e.response.text
                except Exception:
                    detail = e.response.text
                return False, f"Conflict creating folder (e.g. duplicate name in same parent): {detail}", None
            return False, f"Error creating folder: {e.response.status_code} - {e.response.text}", None
        except Exception as e:
            self.logger.error(f"Error in create_folder: {e}", exc_info=True)
            return False, f"Error creating folder: {str(e)}", None

    async def update_folder(
        self,
        folderId: str,
        userPublicId: str,
        name: Optional[str] = None,
        parentId: Optional[str] = None,
    ) -> Tuple[bool, str, Optional[dict]]:
        """Update an existing folder."""
        self.logger.debug(f"update_folder called folderId={folderId}, userPublicId={userPublicId}")
        try:
            row = await self.folders_database.update_folder(
                folderId=folderId,
                userPublicId=userPublicId,
                name=name,
                parentId=parentId,
            )
            if not row:
                return False, "Folder not found", None
            self.logger.info(f"update_folder updated folder id={folderId}")
            return True, "Folder updated successfully", self._row_to_folder(row)
        except Exception as e:
            self.logger.error(f"Error in update_folder: {e}", exc_info=True)
            return False, f"Error updating folder: {str(e)}", None

    async def delete_folder(self, folderId: str, userPublicId: str) -> Tuple[bool, str]:
        """Delete a folder (notes in it will have folder_id set to null)."""
        self.logger.debug(f"delete_folder called folderId={folderId}, userPublicId={userPublicId}")
        try:
            await self.folders_database.delete_folder(folderId, userPublicId)
            return True, "Folder deleted successfully"
        except Exception as e:
            self.logger.error(f"Error in delete_folder: {e}", exc_info=True)
            return False, f"Error deleting folder: {str(e)}"
