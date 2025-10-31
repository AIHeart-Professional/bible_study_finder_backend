from typing import List, Optional
from src.models import (
    BibleTranslationsResponse, BibleBooksResponse, BibleChaptersResponse,
    BibleChapterContentResponse, BibleChapterContentRequest
    )
from src.utils.logger import get_logger
from src.utils.config_loader import load_config
import requests

class BibleService:
    """Service for handling Bible business logic."""
    
    def __init__(self):
        """Initialize the controller and load configuration."""
        self.logger = get_logger(__name__)
        self.config = self._load_config()
        self.base_url = self.config['apis']['bible_api']
        self.api_key = self.config['keys']['bible_api_key']
        print("API Key: " + self.api_key)
        self.headers = {
            'api-key': self.api_key,
            'Content-Type': 'application/json'
        }
        self.logger.info("BiblesController initialized successfully")
    
    def _load_config(self) -> dict:
        """Load configuration from YAML file with environment variable substitution."""
        try:
            config = load_config()
            self.logger.debug("Configuration loaded successfully")
            return config
        except Exception as e:
            self.logger.error(f"Error loading config: {e}")
            # Fallback configuration
            return {
                self.logger.error(f"Error loading config: {e}")
            }
    
    async def get_bibles(self, language: Optional[str] = None) -> List[BibleTranslationsResponse]:
        """Get all available bibles from API.Bible, optionally filtered by language."""
        try:
            # Make API call to get bibles translations
            """ Check if language is provided, if not, get all bibles """
            if language:
                url = f"{self.base_url}/bibles?language={language}"
            else:
                url = f"{self.base_url}/bibles"
            response = requests.get(
                url,
                headers=self.headers,
                timeout=10
            )
            if response.status_code == 200:
                return response.json()['data']
            else:
                self.logger.error(f"API returned status code for bible translations: {response.status_code}: {response.text}")
                return []
        except Exception as e:
            self.logger.error(f"Error fetching bibles from API: {e}")
            return []

    async def _convert_to_bible_response(self, bible_data: dict) -> BibleTranslationsResponse:
        """Convert API.Bible format to our BibleResponse format."""
        return BibleTranslationsResponse(
            id=bible_data.get('id', ''),
            name=bible_data.get('name', ''),
            abbreviation=bible_data.get('abbreviation', ''),
            language='',
        )

    async def get_bible_books(self, bible_id: str) -> List[BibleBooksResponse]:
        """Get all available books in a specific bible."""
        try:
            url = f"{self.base_url}/bibles/{bible_id}/books"
            response = requests.get(
                url,
                headers=self.headers,
                timeout=10
            )
            if response.status_code == 200:
                return response.json()['data']
            else:
                self.logger.error(f"API returned status code for bible books: {response.status_code}: {response.text}")
                return []
        except Exception as e:
            self.logger.error(f"Error fetching bible books from API: {e}")
            return []

    async def _convert_to_bible_book_response(self, bible_book_data: dict) -> BibleBooksResponse:
        """Convert API.Bible format to our BibleBooksResponse format."""
        return BibleBooksResponse(
            id=bible_book_data.get('id', ''),
            name=bible_book_data.get('name', ''),
            abbreviation=bible_book_data.get('abbreviation', ''),
        )

    async def get_bible_chapters(self, bible_id: str, book_id: str) -> List[BibleChaptersResponse]:
        """Get all available chapters in a specific book."""
        try:
            url = f"{self.base_url}/bibles/{bible_id}/books/{book_id}/chapters"
            response = requests.get(
                url,
                headers=self.headers,
                timeout=10
            )
            if response.status_code == 200:
                return response.json()['data']
            else:
                self.logger.error(f"API returned status code for bible chapters: {response.status_code}: {response.text}")
                return []
        except Exception as e:
            self.logger.error(f"Error fetching bible chapters from API: {e}")
            return []

    async def _convert_to_bible_chapter_response(self, bible_chapter_data: dict) -> BibleChaptersResponse:
        """Convert API.Bible format to our BibleChaptersResponse format."""
        return BibleChaptersResponse(
            id=bible_chapter_data.get('id', ''),
            chapter=bible_chapter_data.get('number', ''),
            book=bible_chapter_data.get('bookId', ''),
        )

    async def get_chapter_content(self, bible_id: str, chapter_id: str) -> List[BibleChapterContentResponse]:
        """Get the content of a specific chapter."""
        try:
            url = f"{self.base_url}/bibles/{bible_id}/chapters/{chapter_id}"
            response = requests.get(
                url,
                headers=self.headers,
                timeout=10
            )
            if response.status_code == 200:
                return response.json()['data']
            else:
                self.logger.error(f"API returned status code for chapter content: {response.status_code}: {response.text}")
                return []
        except Exception as e:
            self.logger.error(f"Error fetching chapter content from API: {e}")

    async def _convert_to_bible_chapter_content_response(self, bible_chapter_content_data: dict) -> BibleChapterContentResponse:
        """Convert API.Bible format to our BibleChapterContentResponse format."""
        return BibleChapterContentResponse(
            content=bible_chapter_content_data.get('content', ''),
            verse_count=bible_chapter_content_data.get('verseCount', ''),
        )