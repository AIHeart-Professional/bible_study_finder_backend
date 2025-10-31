#!/usr/bin/env python3
"""
Test script for the Bible Study Finder Backend Logger.
Run this to see the colored logger in action.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.utils.logger import BibleStudyLogger, get_logger
import time

def test_logger():
    """Test the colored logger functionality."""
    
    # Initialize the logger
    BibleStudyLogger.initialize(
        log_level="DEBUG",
        console_output=True,
        file_output=True,
        log_file="logs/test_logger.log"
    )
    
    # Get a logger
    logger = get_logger(__name__)
    
    print("=" * 80)
    print("🎨 TESTING BIBLE STUDY FINDER BACKEND LOGGER")
    print("=" * 80)
    
    # Test different log levels
    logger.debug("🔍 This is a debug message - detailed information for debugging")
    logger.info("ℹ️  This is an info message - general information")
    logger.warning("⚠️  This is a warning message - something unexpected happened")
    logger.error("❌ This is an error message - something went wrong")
    logger.critical("🚨 This is a critical message - serious error occurred")
    
    print("\n" + "=" * 80)
    print("📡 TESTING STRUCTURED LOGGING")
    print("=" * 80)
    
    # Test structured logging methods
    BibleStudyLogger.log_api_call(
        logger, "GET", "https://api.scripture.api.bible/v1/bibles", 
        status_code=200, response_time=0.245
    )
    
    BibleStudyLogger.log_api_call(
        logger, "POST", "https://api.scripture.api.bible/v1/search", 
        status_code=404, error="Endpoint not found"
    )
    
    BibleStudyLogger.log_database_operation(
        logger, "SELECT", "bibles", record_id="123", success=True
    )
    
    BibleStudyLogger.log_database_operation(
        logger, "INSERT", "users", record_id="456", success=False, error="Duplicate key"
    )
    
    BibleStudyLogger.log_business_logic(
        logger, "get_bibles", "Filtering by language", {"language": "English"}
    )
    
    BibleStudyLogger.log_security_event(
        logger, "LOGIN_ATTEMPT", user_id="user123", ip_address="192.168.1.100"
    )
    
    BibleStudyLogger.log_performance(
        logger, "api_call", duration=0.156, memory_usage=45.2
    )
    
    print("\n" + "=" * 80)
    print("🎯 TESTING DIFFERENT LOGGER NAMES")
    print("=" * 80)
    
    # Test different logger names (simulating different modules)
    bible_logger = get_logger("src.controller.bible.bible_controller")
    user_logger = get_logger("src.controller.user.users")
    auth_logger = get_logger("src.controller.auth.authentication")
    
    bible_logger.info("Bible controller initialized")
    user_logger.info("User service started")
    auth_logger.warning("Authentication token expired")
    
    print("\n" + "=" * 80)
    print("✅ LOGGER TEST COMPLETED!")
    print("📁 Check the 'logs/test_logger.log' file for file output")
    print("🎨 Colors should be visible in the console above")
    print("=" * 80)

if __name__ == "__main__":
    test_logger()
