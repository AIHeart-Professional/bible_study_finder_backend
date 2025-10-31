# Bible Study Finder Backend

A FastAPI-based backend service for the Bible Study Finder application.

## Features

- **FastAPI Framework**: Modern, fast web framework for building APIs
- **CORS Configuration**: Proper Cross-Origin Resource Sharing setup
- **RESTful API**: Clean API routes for Bible study resources
- **Pydantic Models**: Data validation and serialization
- **Development Ready**: Hot-reload and debugging support

## Project Structure

```
bible_study_finder_backend/
├── main.py           # Main application entry point
├── api_route.py      # API routes and endpoints
├── cors_config.py    # CORS configuration and bypass settings
├── requirements.txt  # Python dependencies
└── README.md        # This file
```

## Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. **Clone the repository** (if not already done):
   ```bash
   git clone <your-repo-url>
   cd bible_study_finder_backend
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application

1. **Start the development server**:
   ```bash
   python main.py
   ```
   
   Or using uvicorn directly:
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Access the API**:
   - API Base URL: `http://localhost:8000`
   - Interactive API Documentation: `http://localhost:8000/docs`
   - Alternative API Documentation: `http://localhost:8000/redoc`
   - Health Check: `http://localhost:8000/health`

## API Endpoints

### Health & Info
- `GET /` - Root endpoint with API information
- `GET /health` - Health check endpoint

### Bible Study Resources
- `GET /api/v1/resources` - Get all resources (with pagination)
- `GET /api/v1/resources/{id}` - Get specific resource by ID
- `POST /api/v1/resources` - Create new resource
- `PUT /api/v1/resources/{id}` - Update existing resource
- `DELETE /api/v1/resources/{id}` - Delete resource

### Search
- `GET /api/v1/search?q={query}` - Search resources (GET)
- `POST /api/v1/search` - Advanced search (POST)

### Categories & Tags
- `GET /api/v1/categories` - Get all categories
- `GET /api/v1/tags` - Get all available tags

## Configuration

### Environment Variables

Create a `.env` file in the root directory for configuration:

```env
# Environment
ENVIRONMENT=development

# CORS Settings
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:4200
PRODUCTION_ALLOWED_ORIGINS=https://yourdomain.com

# Database (when implemented)
DATABASE_URL=sqlite:///./bible_study.db

# API Settings
API_V1_STR=/api/v1
PROJECT_NAME=Bible Study Finder API
```

### CORS Configuration

The CORS settings are configured in `cors_config.py`:

- **Development**: Allows all origins (`*`) for easy development
- **Production**: Restricts to specified domains for security
- **Configurable**: Uses environment variables for flexibility

## Debugging

### Debug Configurations Available

The project includes multiple debugging options:

#### 1. VS Code Debug Configuration
- Open the project in VS Code
- Go to Run & Debug (Ctrl+Shift+D)
- Select one of the available configurations:
  - **"Debug FastAPI (Uvicorn)"** - Standard debugging
  - **"Debug FastAPI with Uvicorn Module"** - Module-based debugging with reload
  - **"Debug FastAPI (Production Mode)"** - Production-like debugging
  - **"Debug Simple Test Server"** - Fallback simple server

#### 2. Command Line Debug Scripts

**Windows:**
```bash
# Run with batch file
run_debug.bat

# Or directly with Python
python debug_server.py --mode fastapi
python debug_server.py --mode simple
python debug_server.py --mode info
```

**Linux/Mac:**
```bash
# Run with shell script
./run_debug.sh

# Or directly with Python
python3 debug_server.py --mode fastapi
python3 debug_server.py --mode simple
python3 debug_server.py --mode info
```

#### 3. Debug Modes

- **`fastapi`** - Runs the full FastAPI application with debugging
- **`simple`** - Runs a simple HTTP server (fallback for dependency issues)
- **`info`** - Shows system information and dependency status

#### 4. Debug Features

- ✅ **Hot Reload** - Automatically restarts on file changes
- ✅ **Breakpoint Support** - Full debugging with VS Code
- ✅ **Detailed Error Messages** - Enhanced error reporting
- ✅ **CORS Enabled** - Cross-origin requests allowed for development
- ✅ **Environment Variables** - Debug-specific configuration
- ✅ **Dependency Checking** - Automatic dependency validation

#### 5. Troubleshooting

**FastAPI Won't Start:**
- Run `python debug_server.py --mode info` to check dependencies
- Use `python debug_server.py --mode simple` for basic functionality
- Check Python version compatibility (3.10-3.11 recommended)

**Dependency Issues:**
- Install dependencies: `pip install -r requirements.txt`
- For Python 3.13 compatibility issues, create a virtual environment with Python 3.10

**CORS Issues:**
- CORS is automatically configured for development
- Check `cors_config.py` for allowed origins
- Copy `env_example.txt` to `.env` for custom configuration

## Development

### Adding New Endpoints

1. Add your route functions to `api_route.py`
2. Define Pydantic models for request/response validation
3. Include proper error handling with HTTPException
4. Add documentation strings for automatic API docs

### Example Route Addition:

```python
@router.get("/example", response_model=ExampleResponse)
async def get_example():
    """Example endpoint description."""
    return {"message": "Hello World"}
```

### Code Style

The project uses:
- **Black** for code formatting
- **Flake8** for linting
- **MyPy** for type checking

Run code quality checks:
```bash
black .
flake8 .
mypy .
```

### Testing

Run tests using pytest:
```bash
pytest
```

## Deployment

For production deployment:

1. Set `ENVIRONMENT=production` in your environment variables
2. Configure production CORS origins
3. Set up proper database connections
4. Use a production ASGI server like Gunicorn with Uvicorn workers

Example production command:
```bash
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## Next Steps

1. **Database Integration**: Add SQLAlchemy or MongoDB connection
2. **Authentication**: Implement JWT-based authentication
3. **Data Models**: Create actual database models and schemas
4. **Business Logic**: Move business logic to separate service files
5. **Testing**: Add comprehensive test coverage
6. **Logging**: Implement structured logging
7. **Docker**: Add Dockerfile for containerization

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run code quality checks
6. Submit a pull request

## License

This project is licensed under the MIT License.
