"""Bible routes - HTTP layer."""
from typing import List, Optional
from fastapi import APIRouter, Query
from src.models.bible import (
    BibleTranslationsResponse,
    BibleBooksResponse,
    BibleChaptersResponse,
    BibleChapterContentResponse)
from src.controller.bible import BibleController

# Create a router for Bible-related routes
router = APIRouter()


@router.get("/get_bibles", response_model=List[BibleTranslationsResponse])
async def get_bibles(language: str = Query(..., description="Optional language filter (e.g., 'English')")):
    """
    Get all available bibles, optionally filtered by language.
    
    Query Parameters:
        language: Optional language filter (e.g., "English")
    
    Returns:
        List of BibleResponse objects
    """
    results = await BibleController().get_bibles(language)
    return results

@router.get("/get_bible_books", response_model=List[BibleBooksResponse])
async def get_bible_books(bible_id: str = Query(..., description="The ID of the bible to retrieve")):
    """
    Get all available books in a specific bible.
    
    Query Parameters:
        bible_id: The ID of the bible to retrieve
    """
    results = await BibleController().get_bible_books(bible_id)
    return results


@router.get("/get_bible_chapters", response_model=List[BibleChaptersResponse])
async def get_bible_chapters(
    bible_id: str = Query(..., description="The ID of the bible to retrieve"),
    book_id: str = Query(..., description="The ID of the book to retrieve")
):
    """
    Get all available chapters in a specific book.
    
    Query Parameters:
        bible_id: The ID of the bible to retrieve
        book_id: The ID of the book to retrieve
    """
    results = await BibleController().get_bible_chapters(bible_id, book_id)
    return results

@router.get("/get_bible_chapter_content", response_model=BibleChapterContentResponse)
async def get_bible_chapter_content(
    bible_id: str = Query(..., description="The ID of the bible to retrieve"),
    chapter_id: str = Query(..., description="The ID of the chapter to retrieve")
):
    """
    Get the content of a specific chapter and the number of verses in the chapter.
    
    Query Parameters:
        bible_id: The ID of the bible to retrieve
        chapter_id: The ID of the chapter to retrieve
    """
    results = await BibleController().get_bible_chapter_content(bible_id, chapter_id)
    return results

@router.get("/get_bible_chapter_content_by_verse", response_model=BibleChapterContentResponse)
async def get_bible_chapter_content_by_verse(
    bible_id: str = Query(..., description="The ID of the bible to retrieve"),
    chapter_id: str = Query(..., description="The ID of the chapter to retrieve"),
    verse_id: str = Query(..., description="The ID of the verse to retrieve")
):
    """
    Get the content of a specific verse.
    
    Query Parameters:
        bible_id: The ID of the bible to retrieve
        chapter_id: The ID of the chapter to retrieve
        verse_id: The ID of the verse to retrieve
    """
    results = await BibleController().get_bible_chapter_content_by_verse(bible_id, chapter_id, verse_id)
    return results