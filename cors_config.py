"""
CORS configuration for the Bible Study Finder Backend API.
This file handles Cross-Origin Resource Sharing (CORS) settings to bypass restrictions.
"""

import os
from typing import List
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import config

def get_cors_settings() -> dict:
    """
    Get CORS settings for the application.
    
    Returns:
        dict: CORS configuration settings
    """
    
    # Get allowed origins from config
    allowed_origins = config.get_allowed_origins()
    
    # In development mode, allow all origins (less secure but convenient)
    if config.is_development():
        allowed_origins = ["*"]
    
    cors_settings = {
        "allow_origins": allowed_origins,
        "allow_credentials": True,
        "allow_methods": [
            "GET",
            "POST", 
            "PUT",
            "PATCH",
            "DELETE",
            "OPTIONS",
            "HEAD"
        ],
        "allow_headers": [
            "*",  # Allow all headers in development
            "Accept",
            "Accept-Language",
            "Content-Language",
            "Content-Type",
            "Authorization",
            "X-Requested-With",
            "X-CSRF-Token",
            "X-API-Key",
            "User-Agent",
            "Referer",
            "Range"  # Required for PDF streaming
        ],
        "expose_headers": [
            "Content-Range",
            "Accept-Ranges", 
            "Content-Length",
            "Content-Disposition",
            "Content-Type"
        ],
    }
    
    return cors_settings

def get_production_cors_settings() -> dict:
    """
    Get production-ready CORS settings with restricted origins.
    Use this function when deploying to production.
    
    Returns:
        dict: Production CORS configuration settings
    """
    
    # Production allowed origins from config
    production_origins = config.PRODUCTION_ALLOWED_ORIGINS
    
    if not production_origins:
        # Fallback to secure defaults if no production origins specified
        production_origins = [
            "https://yourdomain.com",
            "https://www.yourdomain.com"
        ]
    
    cors_settings = {
        "allow_origins": production_origins,
        "allow_credentials": True,
        "allow_methods": [
            "GET",
            "POST",
            "PUT",
            "PATCH", 
            "DELETE"
        ],
        "allow_headers": [
            "Accept",
            "Accept-Language", 
            "Content-Language",
            "Content-Type",
            "Authorization",
            "X-Requested-With"
        ],
    }
    
    return cors_settings

def setup_cors(app: FastAPI):
    """
    Setup CORS middleware for the FastAPI application.
    This function is called from main.py to configure CORS settings.
    """
    cors_settings = get_cors_settings()
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_settings["allow_origins"],
        allow_credentials=cors_settings["allow_credentials"],
        allow_methods=cors_settings["allow_methods"],
        allow_headers=cors_settings["allow_headers"],
        expose_headers=cors_settings.get("expose_headers", []),
    )
