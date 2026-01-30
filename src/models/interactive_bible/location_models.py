"""Location models for interactive bible feature."""
from typing import List, Optional
from pydantic import BaseModel


class LocationResponse(BaseModel):
	"""Model for location response."""
	id: str
	name: str
	lat: float
	lng: float
	verses: List[str]


class ChapterLocationResponse(BaseModel):
	"""Model for chapter location response."""
	book: str
	chapter: int
	verse: int
	name: str
	longitude: float
	latitude: float


class ChapterCharacterResponse(BaseModel):
	"""
	Model for chapter character response.
	Includes animation timing fields for controlling map icon behavior.
	Optionally includes textbox from verse_dialogue table.
	"""
	name: str
	book: str
	chapter: int
	verse: int
	longitude: float
	latitude: float
	# Animation timing fields
	appear_offset_ms: int = 0
	travel_duration_ms: int = 800
	ease: str = "ease-out"
	# Dialog field from verse_dialogue table (optional)
	textbox: Optional[str] = None


class VerseCharacterResponse(BaseModel):
	"""
	Model for verse character response.
	Includes animation timing fields for controlling map icon behavior.
	Optionally includes textbox from verse_dialogue table.
	"""
	book: str
	chapter: int
	verse: int
	name: str
	longitude: float
	latitude: float
	# Animation timing fields
	appear_offset_ms: int = 0
	travel_duration_ms: int = 800
	ease: str = "ease-out"
	# Dialog field from verse_dialogue table (optional)
	textbox: Optional[str] = None

