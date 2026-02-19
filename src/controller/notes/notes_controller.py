"""Notes controller - Business logic distributor layer."""
from typing import Optional

from src.models.notes import (
    GetNotesResponse,
    GetNoteResponse,
    CreateNoteRequest,
    CreateNoteResponse,
    UpdateNoteRequest,
    UpdateNoteResponse,
    DeleteNoteResponse,
    Note,
)
from src.utils.logger import get_logger
from src.services.notes_service import NotesService


class NotesController:
    """Controller for notes CRUD."""

    def __init__(self):
        """Initialize the controller and notes service."""
        self.logger = get_logger(__name__)
        self.notes_service = NotesService()

    async def list_notes(self, userPublicId: str) -> GetNotesResponse:
        """List all notes for a user (with folder info)."""
        try:
            success, message, notes = await self.notes_service.list_notes(userPublicId)
            note_models = [Note(**n) for n in notes] if notes else []
            return GetNotesResponse(success=success, message=message, notes=note_models)
        except Exception as e:
            self.logger.error(f"Error in list_notes controller: {e}", exc_info=True)
            return GetNotesResponse(success=False, message=str(e), notes=[])

    async def get_note(self, noteId: str, userPublicId: str) -> GetNoteResponse:
        """Get a single note by id (UUID) with folder info."""
        try:
            success, message, note = await self.notes_service.get_note(noteId, userPublicId)
            note_model = Note(**note) if note else None
            return GetNoteResponse(success=success, message=message, note=note_model)
        except Exception as e:
            self.logger.error(f"Error in get_note controller: {e}", exc_info=True)
            return GetNoteResponse(success=False, message=str(e), note=None)

    async def create_note(self, request: CreateNoteRequest) -> CreateNoteResponse:
        """Create a new note (reference normalized; optional folderId)."""
        try:
            success, message, note = await self.notes_service.create_note(
                userPublicId=request.userPublicId,
                reference=request.reference,
                content=request.content,
                tags=request.tags,
                folderId=request.folderId,
            )
            note_model = Note(**note) if note else None
            return CreateNoteResponse(success=success, message=message, note=note_model)
        except Exception as e:
            self.logger.error(f"Error in create_note controller: {e}", exc_info=True)
            return CreateNoteResponse(success=False, message=str(e), note=None)

    async def update_note(self, request: UpdateNoteRequest) -> UpdateNoteResponse:
        """Update an existing note (reference normalized if provided; optional folderId)."""
        try:
            success, message, note = await self.notes_service.update_note(
                noteId=request.noteId,
                userPublicId=request.userPublicId,
                reference=request.reference,
                content=request.content,
                tags=request.tags,
                folderId=request.folderId,
            )
            note_model = Note(**note) if note else None
            return UpdateNoteResponse(success=success, message=message, note=note_model)
        except Exception as e:
            self.logger.error(f"Error in update_note controller: {e}", exc_info=True)
            return UpdateNoteResponse(success=False, message=str(e), note=None)

    async def delete_note(self, noteId: str, userPublicId: str) -> DeleteNoteResponse:
        """Soft-delete a note."""
        try:
            success, message = await self.notes_service.delete_note(noteId, userPublicId)
            return DeleteNoteResponse(success=success, message=message)
        except Exception as e:
            self.logger.error(f"Error in delete_note controller: {e}", exc_info=True)
            return DeleteNoteResponse(success=False, message=str(e))
