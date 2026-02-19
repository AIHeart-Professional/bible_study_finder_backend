"""Folders controller - Business logic distributor layer."""
from typing import Optional

from src.models.notes import (
    GetFoldersResponse,
    GetFolderResponse,
    CreateFolderRequest,
    CreateFolderResponse,
    UpdateFolderRequest,
    UpdateFolderResponse,
    DeleteFolderResponse,
    Folder,
)
from src.utils.logger import get_logger
from src.services.folders_service import FoldersService


class FoldersController:
    """Controller for folders CRUD."""

    def __init__(self):
        """Initialize the controller and folders service."""
        self.logger = get_logger(__name__)
        self.folders_service = FoldersService()

    async def list_folders(self, userPublicId: str) -> GetFoldersResponse:
        """List all folders for a user."""
        try:
            success, message, folders = await self.folders_service.list_folders(userPublicId)
            folder_models = [Folder(**f) for f in folders] if folders else []
            return GetFoldersResponse(success=success, message=message, folders=folder_models)
        except Exception as e:
            self.logger.error(f"Error in list_folders controller: {e}", exc_info=True)
            return GetFoldersResponse(success=False, message=str(e), folders=[])

    async def get_folder(self, folderId: str, userPublicId: str) -> GetFolderResponse:
        """Get a single folder by id (UUID)."""
        try:
            success, message, folder = await self.folders_service.get_folder(folderId, userPublicId)
            folder_model = Folder(**folder) if folder else None
            return GetFolderResponse(success=success, message=message, folder=folder_model)
        except Exception as e:
            self.logger.error(f"Error in get_folder controller: {e}", exc_info=True)
            return GetFolderResponse(success=False, message=str(e), folder=None)

    async def create_folder(self, request: CreateFolderRequest) -> CreateFolderResponse:
        """Create a new folder (optional parentId for hierarchy)."""
        try:
            success, message, folder = await self.folders_service.create_folder(
                userPublicId=request.userPublicId,
                name=request.name,
                parentId=request.parentId,
            )
            folder_model = Folder(**folder) if folder else None
            return CreateFolderResponse(success=success, message=message, folder=folder_model)
        except Exception as e:
            self.logger.error(f"Error in create_folder controller: {e}", exc_info=True)
            return CreateFolderResponse(success=False, message=str(e), folder=None)

    async def update_folder(self, request: UpdateFolderRequest) -> UpdateFolderResponse:
        """Update an existing folder."""
        try:
            success, message, folder = await self.folders_service.update_folder(
                folderId=request.folderId,
                userPublicId=request.userPublicId,
                name=request.name,
                parentId=request.parentId,
            )
            folder_model = Folder(**folder) if folder else None
            return UpdateFolderResponse(success=success, message=message, folder=folder_model)
        except Exception as e:
            self.logger.error(f"Error in update_folder controller: {e}", exc_info=True)
            return UpdateFolderResponse(success=False, message=str(e), folder=None)

    async def delete_folder(self, folderId: str, userPublicId: str) -> DeleteFolderResponse:
        """Delete a folder (notes in it will have folder_id set to null)."""
        try:
            success, message = await self.folders_service.delete_folder(folderId, userPublicId)
            return DeleteFolderResponse(success=success, message=message)
        except Exception as e:
            self.logger.error(f"Error in delete_folder controller: {e}", exc_info=True)
            return DeleteFolderResponse(success=False, message=str(e))
