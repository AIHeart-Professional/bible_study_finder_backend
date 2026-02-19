"""Notes and folders routes - HTTP layer for users_notes and users_folders CRUD."""
from fastapi import APIRouter, Query

from src.models.notes import (
    GetNotesResponse,
    GetNoteResponse,
    CreateNoteRequest,
    CreateNoteResponse,
    UpdateNoteRequest,
    UpdateNoteResponse,
    DeleteNoteResponse,
    GetFoldersResponse,
    GetFolderResponse,
    CreateFolderRequest,
    CreateFolderResponse,
    UpdateFolderRequest,
    UpdateFolderResponse,
    DeleteFolderResponse,
)
from src.controller.notes import NotesController, FoldersController

router = APIRouter()


# --- Notes ---

@router.get("/get_notes", response_model=GetNotesResponse)
async def get_notes(
    userPublicId: str = Query(..., description="User public_id (UUID)"),
):
    """List all notes for a user (excluding soft-deleted), with folder info."""
    return await NotesController().list_notes(userPublicId=userPublicId)


@router.get("/get_note", response_model=GetNoteResponse)
async def get_note(
    userPublicId: str = Query(..., description="User public_id (UUID)"),
    noteId: str = Query(..., description="Note id (UUID)"),
):
    """Get a single note by id with folder info."""
    return await NotesController().get_note(noteId=noteId, userPublicId=userPublicId)


@router.post("/create_note", response_model=CreateNoteResponse)
async def create_note(request: CreateNoteRequest):
    """Create a note. Reference is normalized; optional folderId."""
    return await NotesController().create_note(request=request)


@router.put("/update_note", response_model=UpdateNoteResponse)
async def update_note(request: UpdateNoteRequest):
    """Update a note. If reference is provided, it is normalized; optional folderId."""
    return await NotesController().update_note(request=request)


@router.delete("/delete_note", response_model=DeleteNoteResponse)
async def delete_note(
    userPublicId: str = Query(..., description="User public_id (UUID)"),
    noteId: str = Query(..., description="Note id (UUID)"),
):
    """Soft-delete a note (sets deleted_at)."""
    return await NotesController().delete_note(noteId=noteId, userPublicId=userPublicId)


# --- Folders ---

@router.get("/get_folders", response_model=GetFoldersResponse)
async def get_folders(
    userPublicId: str = Query(..., description="User public_id (UUID)"),
):
    """List all folders for a user."""
    return await FoldersController().list_folders(userPublicId=userPublicId)


@router.get("/get_folder", response_model=GetFolderResponse)
async def get_folder(
    userPublicId: str = Query(..., description="User public_id (UUID)"),
    folderId: str = Query(..., description="Folder id (UUID)"),
):
    """Get a single folder by id."""
    return await FoldersController().get_folder(folderId=folderId, userPublicId=userPublicId)


@router.post("/create_folder", response_model=CreateFolderResponse)
async def create_folder(request: CreateFolderRequest):
    """Create a folder (optional parentId for hierarchy)."""
    return await FoldersController().create_folder(request=request)


@router.put("/update_folder", response_model=UpdateFolderResponse)
async def update_folder(request: UpdateFolderRequest):
    """Update a folder (name and/or parentId)."""
    return await FoldersController().update_folder(request=request)


@router.delete("/delete_folder", response_model=DeleteFolderResponse)
async def delete_folder(
    userPublicId: str = Query(..., description="User public_id (UUID)"),
    folderId: str = Query(..., description="Folder id (UUID)"),
):
    """Delete a folder. Notes in it will have folder_id set to null."""
    return await FoldersController().delete_folder(folderId=folderId, userPublicId=userPublicId)
