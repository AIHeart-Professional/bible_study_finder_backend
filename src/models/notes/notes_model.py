"""Notes and folders request/response models."""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class FolderInfo(BaseModel):
    """Folder summary embedded in a note response."""

    id: str  # UUID
    name: str
    parentId: Optional[str] = None  # UUID


class Note(BaseModel):
    """Model for a user note."""

    id: str  # UUID
    userPublicId: str
    reference: str
    normalizedReference: Optional[str] = None
    content: str
    tags: List[str] = []
    folderId: Optional[str] = None
    folder: Optional[FolderInfo] = None
    createdAt: datetime
    updatedAt: datetime


# --- Notes requests/responses ---

class GetNotesResponse(BaseModel):
    success: bool
    message: str
    notes: List[Note] = []


class GetNoteResponse(BaseModel):
    success: bool
    message: str
    note: Optional[Note] = None


class CreateNoteRequest(BaseModel):
    userPublicId: str
    reference: str
    content: str
    tags: Optional[List[str]] = None
    folderId: Optional[str] = None


class CreateNoteResponse(BaseModel):
    success: bool
    message: str
    note: Optional[Note] = None


class UpdateNoteRequest(BaseModel):
    userPublicId: str
    noteId: str  # UUID
    reference: Optional[str] = None
    content: Optional[str] = None
    tags: Optional[List[str]] = None
    folderId: Optional[str] = None


class UpdateNoteResponse(BaseModel):
    success: bool
    message: str
    note: Optional[Note] = None


class DeleteNoteResponse(BaseModel):
    success: bool
    message: str


# --- Folders ---

class Folder(BaseModel):
    """Model for a user folder."""

    id: str  # UUID
    userPublicId: str
    name: str
    parentId: Optional[str] = None
    createdAt: datetime
    updatedAt: datetime


class GetFoldersResponse(BaseModel):
    success: bool
    message: str
    folders: List[Folder] = []


class GetFolderResponse(BaseModel):
    success: bool
    message: str
    folder: Optional[Folder] = None


class CreateFolderRequest(BaseModel):
    userPublicId: str
    name: str
    parentId: Optional[str] = None


class CreateFolderResponse(BaseModel):
    success: bool
    message: str
    folder: Optional[Folder] = None


class UpdateFolderRequest(BaseModel):
    userPublicId: str
    folderId: str  # UUID
    name: Optional[str] = None
    parentId: Optional[str] = None


class UpdateFolderResponse(BaseModel):
    success: bool
    message: str
    folder: Optional[Folder] = None


class DeleteFolderResponse(BaseModel):
    success: bool
    message: str
