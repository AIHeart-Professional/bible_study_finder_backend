"""
Debug launcher for Bible Study Finder Backend API.
This script provides easy debugging capabilities for the FastAPI application.
"""

import os
import sys
import uvicorn
from pathlib import Path

# Add current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Set debug environment variables
os.environ["DEBUG"] = "true"
os.environ["ENVIRONMENT"] = "development"
os.environ["PYTHONPATH"] = str(current_dir)

def run_debug_server():
    """
    Run the FastAPI server in debug mode with enhanced debugging capabilities.
    """
    print("Starting Bible Study Finder API in DEBUG mode...")
    print("=" * 60)
    print(f"Working Directory: {current_dir}")
    print(f"Python Path: {sys.path[0]}")
    print(f"Server will be available at: http://localhost:8000")
    print(f"API Docs will be available at: http://localhost:8000/docs")
    print("=" * 60)
    print()
    print("Debug Features Enabled:")
    print("- Hot reload on file changes")
    print("- Detailed error messages") 
    print("- Debug logging")
    print("- CORS enabled for development")
    print()
    print("Press Ctrl+C to stop the server")
    print("=" * 60)
    
    try:
        # Import and setup app
        from main import app
        
        # Run uvicorn with debug settings
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="debug",
            access_log=True,
            use_colors=True,
            reload_dirs=[str(current_dir)],
            reload_includes=["*.py"],
            reload_excludes=["__pycache__/*", "*.pyc", ".vscode/*", ".git/*"]
        )
    except ImportError as e:
        print(f"Import Error: {e}")
        print()
        print("Falling back to simple test server...")
        print("=" * 60)
        
        try:
            from simple_test import run_server
            run_server()
        except ImportError:
            print("Neither FastAPI nor simple test server could be imported")
            print("Please check your dependencies and Python path")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Error starting server: {e}")
        print("Check your configuration and dependencies")
        sys.exit(1)

def run_simple_debug():
    """
    Run the simple test server for debugging when FastAPI has issues.
    """
    print("Starting Simple Test Server in DEBUG mode...")
    print("=" * 60)
    
    try:
        from simple_test import run_server
        run_server()
    except ImportError as e:
        print(f"Could not import simple test server: {e}")
        sys.exit(1)

def show_debug_info():
    """
    Show debugging information about the current environment.
    """
    print("Debug Information")
    print("=" * 60)
    print(f"Python Version: {sys.version}")
    print(f"Python Executable: {sys.executable}")
    print(f"Current Directory: {current_dir}")
    print(f"Python Path: {sys.path}")
    print()
    
    print("Environment Variables:")
    debug_vars = ["DEBUG", "ENVIRONMENT", "PYTHONPATH", "PATH"]
    for var in debug_vars:
        value = os.environ.get(var, "Not set")
        print(f"  {var}: {value[:100]}{'...' if len(str(value)) > 100 else ''}")
    print()
    
    print("Checking Dependencies:")
    dependencies = ["fastapi", "uvicorn", "pydantic", "starlette"]
    for dep in dependencies:
        try:
            __import__(dep)
            print(f"  [OK] {dep}: Available")
        except ImportError as e:
            print(f"  [MISSING] {dep}: Missing - {e}")
        except Exception as e:
            print(f"  [ERROR] {dep}: Error loading - {e}")
    
    print()
    print("Project Files:")
    files = ["main.py", "cors_config.py", "src/models/models.py", "simple_test.py"]
    for file in files:
        file_path = current_dir / file
        if file_path.exists():
            print(f"  [OK] {file}: Found")
        else:
            print(f"  [MISSING] {file}: Missing")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Bible Study Finder API Debug Launcher")
    parser.add_argument("--mode", choices=["fastapi", "simple", "info"], 
                       default="fastapi", help="Debug mode to run")
    parser.add_argument("--port", type=int, default=8000, 
                       help="Port to run server on")
    
    args = parser.parse_args()
    
    if args.mode == "info":
        show_debug_info()
    elif args.mode == "simple":
        run_simple_debug()
    else:
        run_debug_server()
