"""Bible routes - HTTP layer."""
from typing import List, Optional
from fastapi import APIRouter, Query
from src.models import (
    BibleTranslationsResponse, BibleTranslationsRequest, 
    BibleBooksResponse, BibleBooksRequest, 
    BibleChaptersResponse, BibleChaptersRequest,
    BibleChapterContentResponse, BibleChapterContentRequest,
    BibleChapterContentByVerseRequest)
from src.controller.bible.bible_controller import BiblesController

# Create a router for Bible-related routes
router = APIRouter()


@router.get("/get_bibles", response_model=List[BibleTranslationsResponse])
async def get_bibles(BibleTranslationsRequest: BibleTranslationsRequest):
    """
    Get all available bibles, optionally filtered by language.
    
    Query Parameters:
        language: Optional language filter (e.g., "English")
    
    Returns:
        List of BibleResponse objects
    """
    results = await BiblesController().get_bibles(BibleTranslationsRequest.language)
    return results

@router.get("/get_bible_books", response_model=List[BibleBooksResponse])
async def get_bible_books(BibleBooksRequest: BibleBooksRequest):
    """
    Get all available books in a specific bible.
    
    Query Parameters:
        bible_id: The ID of the bible to retrieve
    """
    results = await BiblesController().get_bible_books(BibleBooksRequest.bible_id)
    return results


@router.get("/get_bible_chapters", response_model=List[BibleChaptersResponse])
async def get_bible_chapters(BibleChaptersRequest: BibleChaptersRequest):
    """
    Get all available chapters in a specific book.
    
    Query Parameters:
        bible_id: The ID of the bible to retrieve
        book_id: The ID of the book to retrieve
    """
    results = await BiblesController().get_bible_chapters(BibleChaptersRequest.bible_id, BibleChaptersRequest.book_id)
    return results

@router.get("/get_bible_chapter_content", response_model=BibleChapterContentResponse)
async def get_bible_chapter_content(BibleChapterContentRequest: BibleChapterContentRequest):
    """
    Get the content of a specific chapter and the number of verses in the chapter.
    
    Query Parameters:
        bible_id: The ID of the bible to retrieve
        chapter_id: The ID of the chapter to retrieve
    """
    results = await BiblesController().get_bible_chapter_content(BibleChapterContentRequest.bible_id, BibleChapterContentRequest.chapter_id)
    return results

@router.get("/get_bible_chapter_content_by_verse", response_model=BibleChapterContentResponse)
async def get_bible_chapter_content_by_verse(BibleChapterContentByVerseRequest: BibleChapterContentByVerseRequest):
    """
    Get the content of a specific verse.
    
    Query Parameters:
        bible_id: The ID of the bible to retrieve
        verse_id: The ID of the verse to retrieve
    """
    results = await BiblesController().get_bible_chapter_content_by_verse(BibleChapterContentByVerseRequest.bible_id, BibleChapterContentByVerseRequest.chapter_id, BibleChapterContentByVerseRequest.verse_id)
    return results