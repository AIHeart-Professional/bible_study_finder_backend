# Architecture Guide

## Recommended Structure: Controller-Based Routes

This project uses a **controller-based architecture** where each controller is responsible for its own routes using FastAPI's `APIRouter`.

### Structure

```
src/
├── controller/
│   └── bible/
│       └── bibles.py          # Bible business logic
├── routes/
│   └── bible/
│       └── bible_routes.py   # HTTP routes for Bible
├── models/
│   └── models.py              # Pydantic models
└── services/                  # Service layer (future)

api_route.py                   # Central route registration
main.py                        # Application entry point
config.py                      # Configuration
```

### How It Works

1. **Routes** (`src/routes/`) define HTTP endpoints using FastAPI's `APIRouter`
2. **Controllers** (`src/controller/`) handle business logic and call services
3. **Routers are included in api_route.py**
4. **Main.py creates the app and registers everything**

### Separation of Concerns

- **Routes**: HTTP-specific (request/response handling, validation)
- **Controllers**: Business logic (data processing, validation)
- **Services**: External integrations (database, APIs)

### Example: Bible Routes and Controller

```python
# src/routes/bible/bible_routes.py
from fastapi import APIRouter
from src.controller.bible.bibles import BiblesController

router = APIRouter(prefix="/bible", tags=["bible"])
bible_controller = BiblesController()

@router.get("", response_model=List[BibleResponse])
async def get_bibles(language: str = None):
    return await bible_controller.get_bibles(language)

# src/controller/bible/bibles.py
class BiblesController:
    async def get_bibles(self, language: str = None):
        # Business logic here
        return mock_data
```

### Registering Routers

```python
# api_route.py
from src.controller.bible.bibles import router as bible_router

def setup_routes(app: FastAPI):
    app.include_router(bible_router)
    # Add more routers as needed
```

### Benefits

✅ **Modular**: Each controller is self-contained  
✅ **Scalable**: Add new features by creating new controllers  
✅ **Organized**: Related code stays together  
✅ **Testable**: Easy to test individual controllers  
✅ **Maintainable**: Clear separation of concerns  

### Best Practices

1. **One router per resource** (e.g., Bible router, Group router, Church router)
2. **Keep route handlers thin** - delegate business logic to services
3. **Use dependency injection** for database connections, etc.
4. **Document your routes** with docstrings and response models
5. **Group related routes** with prefixes and tags

### Migration Path

As you add more controllers:

1. Create `src/controller/groups/groups.py` → Create router → Register in api_route.py
2. Create `src/controller/churches/churches.py` → Create router → Register in api_route.py
3. Create `src/controller/study/study.py` → Create router → Register in api_route.py

Each controller manages its own routes independently!

