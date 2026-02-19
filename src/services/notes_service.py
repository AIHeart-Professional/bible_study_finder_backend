"""Notes service - Application logic layer for user notes."""
import json
from typing import List, Optional, Tuple

import httpx
from src.utils.logger import get_logger
from src.utils.reference_formatter import format_reference
from src.database.notes.notes_database import NotesDatabase
from src.database.notes.folders_database import FoldersDatabase


class NotesService:
    """Service for user notes CRUD and reference formatting."""

    def __init__(self):
        """Initialize the service and database."""
        self.logger = get_logger(__name__)
        self.notes_database = NotesDatabase()
        self.folders_database = FoldersDatabase()
        self.logger.info("NotesService initialized successfully")

    def _parse_datetime(self, dt_value) -> Optional[str]:
        """Return ISO string for API; accept datetime or str."""
        if dt_value is None:
            return None
        if hasattr(dt_value, "isoformat"):
            return dt_value.isoformat()
        if isinstance(dt_value, str):
            return dt_value
        return str(dt_value)

    def _row_to_note(self, row: dict, folder: Optional[dict] = None) -> dict:
        """Map DB row to note dict for response; optionally attach folder info."""
        folder_id = row.get("folder_id")
        folder_info = None
        if folder:
            folder_info = {
                "id": folder["id"],
                "name": folder["name"],
                "parentId": folder.get("parent_id"),
            }
        return {
            "id": str(row["id"]),
            "userPublicId": str(row["user_id"]),
            "reference": row.get("reference", ""),
            "normalizedReference": row.get("normalized_reference"),
            "content": row.get("content", ""),
            "tags": row.get("tags") or [],
            "folderId": str(folder_id) if folder_id else None,
            "folder": folder_info,
            "createdAt": self._parse_datetime(row.get("created_at")),
            "updatedAt": self._parse_datetime(row.get("updated_at")),
        }

    async def list_notes(self, userPublicId: str) -> Tuple[bool, str, List[dict]]:
        """List all notes for a user with folder info attached."""
        self.logger.debug(f"list_notes called userPublicId={userPublicId}")
        try:
            rows = await self.notes_database.list_notes(userPublicId)
            folder_ids = list({str(r["folder_id"]) for r in rows if r.get("folder_id")})
            folders = await self.folders_database.get_folders_by_ids(folder_ids) if folder_ids else []
            folder_map = {str(f["id"]): f for f in folders}
            notes = [
                self._row_to_note(r, folder_map.get(str(r["folder_id"])) if r.get("folder_id") else None)
                for r in rows
            ]
            self.logger.info(f"list_notes returned {len(notes)} notes")
            return True, "Notes retrieved successfully", notes
        except Exception as e:
            self.logger.error(f"Error in list_notes: {e}", exc_info=True)
            return False, f"Error retrieving notes: {str(e)}", []

    async def get_note(self, noteId: str, userPublicId: str) -> Tuple[bool, str, Optional[dict]]:
        """Get a single note by id with folder info."""
        self.logger.debug(f"get_note called noteId={noteId}, userPublicId={userPublicId}")
        try:
            row = await self.notes_database.get_note_by_id(noteId, userPublicId)
            if not row:
                return False, "Note not found", None
            folder = None
            if row.get("folder_id"):
                folder = await self.folders_database.get_folder_by_id(str(row["folder_id"]), userPublicId)
            return True, "Note retrieved successfully", self._row_to_note(row, folder)
        except Exception as e:
            self.logger.error(f"Error in get_note: {e}", exc_info=True)
            return False, f"Error retrieving note: {str(e)}", None

    async def create_note(
        self,
        userPublicId: str,
        reference: str,
        content: str,
        tags: Optional[List[str]] = None,
        folderId: Optional[str] = None,
    ) -> Tuple[bool, str, Optional[dict]]:
        """Create a note. Reference is stored as-is; normalized form in normalized_reference."""
        self.logger.debug(f"create_note called userPublicId={userPublicId}")
        normalized_ref = format_reference(reference)
        try:
            row = await self.notes_database.create_note(
                userPublicId=userPublicId,
                reference=reference,
                normalized_reference=normalized_ref,
                content=content,
                tags=tags,
                folderId=folderId,
            )
            if not row:
                return False, "Failed to create note", None
            folder = None
            if row.get("folder_id"):
                folder = await self.folders_database.get_folder_by_id(str(row["folder_id"]), userPublicId)
            self.logger.info(f"create_note created note id={row.get('id')}")
            return True, "Note created successfully", self._row_to_note(row, folder)
        except httpx.HTTPStatusError as e:
            self.logger.error(f"Error in create_note: {e.response.status_code} - {e.response.text}", exc_info=True)
            if e.response.status_code == 409:
                try:
                    body = e.response.json()
                    detail = body.get("message") or body.get("details") or e.response.text
                except Exception:
                    detail = e.response.text
                return False, f"Conflict creating note (duplicate or constraint): {detail}", None
            return False, f"Error creating note: {e.response.status_code} - {e.response.text}", None
        except Exception as e:
            self.logger.error(f"Error in create_note: {e}", exc_info=True)
            return False, f"Error creating note: {str(e)}", None

    async def update_note(
        self,
        noteId: str,
        userPublicId: str,
        reference: Optional[str] = None,
        content: Optional[str] = None,
        tags: Optional[List[str]] = None,
        folderId: Optional[str] = None,
    ) -> Tuple[bool, str, Optional[dict]]:
        """Update a note. If reference is provided, normalized form is updated too."""
        self.logger.debug(f"update_note called noteId={noteId}, userPublicId={userPublicId}")
        normalized_ref = format_reference(reference) if reference is not None else None
        try:
            row = await self.notes_database.update_note(
                noteId=noteId,
                userPublicId=userPublicId,
                reference=reference,
                normalized_reference=normalized_ref,
                content=content,
                tags=tags,
                folderId=folderId,
            )
            if not row:
                return False, "Note not found", None
            folder = None
            if row.get("folder_id"):
                folder = await self.folders_database.get_folder_by_id(str(row["folder_id"]), userPublicId)
            self.logger.info(f"update_note updated note id={noteId}")
            return True, "Note updated successfully", self._row_to_note(row, folder)
        except Exception as e:
            self.logger.error(f"Error in update_note: {e}", exc_info=True)
            return False, f"Error updating note: {str(e)}", None

    async def delete_note(self, noteId: str, userPublicId: str) -> Tuple[bool, str]:
        """Soft-delete a note."""
        self.logger.debug(f"delete_note called noteId={noteId}, userPublicId={userPublicId}")
        try:
            ok = await self.notes_database.soft_delete_note(noteId, userPublicId)
            if not ok:
                return False, "Note not found"
            return True, "Note deleted successfully"
        except Exception as e:
            self.logger.error(f"Error in delete_note: {e}", exc_info=True)
            return False, f"Error deleting note: {str(e)}"
