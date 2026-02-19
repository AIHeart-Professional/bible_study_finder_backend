"""
Main entry point for the Bible Study Finder Backend API.
"""

import uvicorn
from cors_config import setup_cors
from config import config
from src.routes import bible_routes, users_routes, groups_routes, roles_routes, interactive_bible_routes, notes_routes
from src.utils.logger import BibleStudyLogger, get_logger
from fastapi import FastAPI

# Initialize logging system
BibleStudyLogger.initialize(
    log_level="DEBUG" if config.DEBUG else "INFO",
    console_output=True,
    file_output=True,
    log_file="logs/bible_study_backend.log"
)

# Get logger for main module
logger = get_logger(__name__)

# Create the FastAPI app
app = FastAPI()

# Add routes
app.include_router(bible_routes.router, prefix="/bible", tags=["bible"])
app.include_router(users_routes.router, prefix="/users", tags=["users"])
app.include_router(groups_routes.router, prefix="/groups", tags=["groups"])
app.include_router(roles_routes.router, prefix="/roles", tags=["roles"])
app.include_router(interactive_bible_routes.router, prefix="/interactive_bible", tags=["interactive_bible"])
app.include_router(notes_routes.router, prefix="/notes", tags=["notes"])

# Setup CORS
setup_cors(app)

@app.get("/")
async def root():
    logger.info("Root endpoint accessed")
    return {"message": "Bible Study Finder Backend API is running"}

if __name__ == "__main__":
    logger.info("Starting Bible Study Finder Backend API")
    logger.info(f"Debug mode: {config.DEBUG}")
    logger.info(f"Environment: {config.ENVIRONMENT}")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=config.DEBUG,
        log_level="debug" if config.DEBUG else "info"
    )