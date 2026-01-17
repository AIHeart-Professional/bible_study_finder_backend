"""Location models for interactive bible feature."""
from typing import List
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
	"""Model for chapter character response."""
	name: str
	book: str
	chapter: int
	verse: int
	longitude: float
	latitude: float

class VerseCharacterResponse(BaseModel):
	"""Model for verse character response."""
	book: str
	chapter: int
	verse: int
	name: str
	longitude: float
	latitude: float

