"""Bible controller - Business logic layer."""
from typing import List, Optional
from src.models import (BibleTranslationsResponse, BibleBooksResponse, 
BibleChaptersResponse, BibleChapterContentResponse, BibleChapterContentByVerseResponse)
from src.utils.logger import get_logger
from src.services.bible_service import BibleService

class BiblesController:
    """Controller for handling Bible business logic."""
    
    def __init__(self):
        """Initialize the controller and Bible service."""
        self.bible_service = BibleService()
        self.logger = get_logger(__name__)

    async def get_bibles(self, language: Optional[str] = None) -> List[BibleTranslationsResponse]:
        """
        Get all available bibles from API.Bible, optionally filtered by language.
        
        Args:
            language: Optional language filter
            
        Returns:
            List of BibleResponse objects
        """
        try:
            formatted_bibles = []
            bibles_data = await self.bible_service.get_bibles(language)
            for bible in bibles_data:
                formatted_bibles.append(await BibleService()._convert_to_bible_response(bible))
            return formatted_bibles
        except Exception as e:
            self.logger.error(f"Error fetching bibles from API: {e}")
            return []  
    
    async def get_bible_books(self, bible_id: str) -> List[BibleBooksResponse]:
        """
        Get all available books in a specific bible.
        
        Args:
            bible_id: The ID of the bible to retrieve
        """
        try:
            formatted_bible_books = []
            bible_books_data = await self.bible_service.get_bible_books(bible_id)
            for bible_book in bible_books_data:
                formatted_bible_books.append(await BibleService()._convert_to_bible_book_response(bible_book))
            return formatted_bible_books
        except Exception as e:
            self.logger.error(f"Error fetching bible books from API: {e}")
            return []

    async def get_bible_chapters(self, bible_id: str, book_id: str) -> List[BibleChaptersResponse]:
        """
        Get all available chapters in a specific book.
        
        Args:
            bible_id: The ID of the bible to retrieve
            book_id: The ID of the book to retrieve
        """
        try:
            formatted_bible_chapters = []
            bible_chapters_data = await self.bible_service.get_bible_chapters(bible_id, book_id)
            for bible_chapter in bible_chapters_data:
                formatted_bible_chapters.append(await BibleService()._convert_to_bible_chapter_response(bible_chapter))
            return formatted_bible_chapters
        except Exception as e:
            self.logger.error(f"Error fetching bible chapters from API: {e}")
            return []

    async def get_bible_chapter_content(self, bible_id: str, chapter_id: str) -> BibleChapterContentResponse:
        """
        Get the content of a specific chapter and the number of verses in the chapter.
        
        Args:
            bible_id: The ID of the bible to retrieve
            chapter_id: The ID of the chapter to retrieve
        """
        try:
            content = await self.bible_service.get_chapter_content(bible_id, chapter_id)
            return await BibleService()._convert_to_bible_chapter_content_response(content)
        except Exception as e:
            self.logger.error(f"Error fetching bible chapter content from API: {e}")
            return []   

    async def get_bible_chapter_content_by_verse(self, bible_id: str, verse_id: str) -> BibleChapterContentResponse:
        """
        Get the content of a specific verse.
        
        Args:
            bible_id: The ID of the bible to retrieve
            chapter_id: The ID of the chapter to retrieve
            verse_id: The ID of the verse to retrieve
        """
        try:
            content = await self.bible_service.get_chapter_content_by_verse(bible_id, chapter_id, verse_id)
            return await BibleService()._convert_to_bible_chapter_content_by_verse_response(content)
        except Exception as e:
            self.logger.error(f"Error fetching bible chapter content by verse from API: {e}")
            return []