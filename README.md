# FastAPI Application

This README provides instructions on how to set up and run the FastAPI application.

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Virtual environment (recommended)

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <repository-url>
cd <project-directory>
```

### 2. Create and Activate a Virtual Environment (Optional but Recommended)

**For Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**For macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

Install all required packages from the `requirements.txt` file:

```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

Create a `.env` file in the project root directory with the following variables:

```
# Database Configuration
DATABASE_URL=postgresql+asyncpg://username:password@localhost:5432/database_name

# Security Settings
SECRET_KEY=your_secret_key_here
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Optional Settings
DEBUG=True
LOG_LEVEL=INFO

# Example API Keys (if needed)
# EXTERNAL_API_KEY=your_api_key_here
```

Make sure to replace the placeholder values with your actual configuration:

- `DATABASE_URL`: Your database connection string
- `SECRET_KEY`: A secure random string used for encryption
- `ACCESS_TOKEN_EXPIRE_MINUTES`: How long JWT tokens remain valid

### 5. Run the Application

You can run the FastAPI application using Uvicorn:

```bash
uvicorn app.main:app --reload
```

- `app.main:app` refers to the `app` object in `main.py` file inside the `app` package
- `--reload` enables auto-reload on code changes (recommended for development)

Additional Uvicorn options:
- Specify port: `--port 8080`
- Specify host (to allow external access): `--host 0.0.0.0`

For production deployment:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 6. Access the Application

Once running, you can access:
- API: http://localhost:8000
- Interactive API documentation: http://localhost:8000/docs  SWAGGER UI
- Alternative API documentation: http://localhost:8000/endpoints at Postman

## Running Tests

To run the tests:

```bash
pytest
```

For more detailed test output:

```bash
pytest -v
```

## Troubleshooting

If you encounter any issues:

1. Ensure all dependencies are installed correctly
2. Verify the `.env` file contains all required variables
3. Check database connection and credentials
4. Examine the application logs for detailed error messages

## Project Structure

```
app/
├── main.py                           # Application entry point
├── app_configs/                      # configurations for the app
├── authentications/                  # Authentication and authorization
├── db/                               # Database models and connections
├── schemas/                          # Pydantic models
└── routers/                          # API endpoints
    ├── __init__.py
    ├── users.py
    ├──  workouts.py
    ├── progress.py 
    └── goals.py
├── tests/                             # Tests
    ├── __init__.py
    ├── conftest.py                    # Test configuration
    ├── test_security.py
    └── routers/                        # Test cases for endpoints
        ├── __init__.py
        ├── test_goals.py
        ├── test_progress.py
        ├── test_user.py 
        └── test_workouts.py
├──.env                                 # Environment variables
├──.env.example                         # Example environment variables
├──.gitignore                           # Git ignore file
├──my_fit_logger.log                    # recorded logs 
├──.pre-commit-config.yaml              # Pre-commit hooks configuration
├──requirements.txt                     # Project dependencies
├──requirements-dev.txt                 # Development dependencies







```