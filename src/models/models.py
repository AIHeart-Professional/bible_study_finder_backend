"""
Pydantic models for the Bible Study Finder Backend API.
Contains all data models for request/response validation.
"""

from typing import List, Optional
from pydantic import BaseModel

class BibleStudyResource(BaseModel):
    """Model for Bible study resource data."""
    id: int
    title: str
    description: str
    category: str
    author: str
    url: Optional[str] = None
    tags: List[str] = []

class SearchQuery(BaseModel):
    """Model for search query requests."""
    query: str
    category: Optional[str] = None
    tags: Optional[List[str]] = []
    limit: Optional[int] = 10

class CreateResourceRequest(BaseModel):
    """Model for creating new Bible study resources."""
    title: str
    description: str
    category: str
    author: str
    url: Optional[str] = None
    tags: List[str] = []

class UpdateResourceRequest(BaseModel):
    """Model for updating existing Bible study resources."""
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    author: Optional[str] = None
    url: Optional[str] = None
    tags: Optional[List[str]] = None

class BibleTranslationsRequest(BaseModel):
    """Model for a Bible request."""
    language: str

class BibleTranslationsResponse(BaseModel):
    """Model for a Bible response."""
    id: str
    name: str
    abbreviation: str
    language: str

class BibleBooksRequest(BaseModel):
    """Model for a Bible books request."""
    bible_id: str

class BibleBooksResponse(BaseModel):
    """Model for a Bible books response."""
    id: str
    name: str
    abbreviation: str

class BibleChaptersRequest(BaseModel):
    """Model for a Bible chapters request."""
    bible_id: str
    book_id: str

class BibleChaptersResponse(BaseModel):
    """Model for a Bible chapters response."""
    id: str
    chapter: str
    book: str

class BibleChapterContentRequest(BaseModel):
    """Model for a Bible chapter content request."""
    bible_id: str
    chapter_id: str

class BibleChapterContentResponse(BaseModel):
    """Model for a Bible chapter content response."""
    content: str
    verse_count: str

class CategoryResponse(BaseModel):
    """Model for category list response."""
    categories: List[str]

class TagResponse(BaseModel):
    """Model for tag list response."""
    tags: List[str]

class HealthResponse(BaseModel):
    """Model for health check response."""
    status: str

class RootResponse(BaseModel):
    """Model for root endpoint response."""
    message: str
    status: str
    version: str

class CreateGroupRequest(BaseModel):
    """Model for creating a new group."""
    name: str
    description: Optional[str] = None
    leader: str
    location: str
    meeting_details: str
    group_type: str
    capacity: int
    tags: Optional[List[str]] = None
    active_status: bool
    online_meeting: bool
    languages: List[str]
    age_range: str
    accessibility: List[str]
    


class Group(BaseModel):
    """Model for a group."""
    id: int
    name: str
    description: str