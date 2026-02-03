#!/usr/bin/env python3
"""
Local FastAPI server for testing the AWS Lambda document extraction function.

This script wraps the Lambda handler in a FastAPI server to enable local testing
and development without deploying to AWS Lambda.

Usage:
    python run_locally.py

The server will start on http://localhost:8000

API Endpoints:
    POST /extract - Extract text from a PDF document
        Request body: {"path": "path/to/document.pdf"}
        Response: JSON with extraction results or error details

Requirements:
    - Set environment variables for AWS S3 access
    - FastAPI and Uvicorn (already in requirements.txt)
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, Any

# Load environment variables from .env file first
def load_env_manually(env_file_path):
    """Manually load environment variables from .env file."""
    if not os.path.exists(env_file_path):
        return False
    
    print(f"📋 Loading environment variables from {env_file_path}")
    
    with open(env_file_path, 'r') as f:
        for line in f:
            line = line.strip()
            
            # Skip empty lines and comments
            if not line or line.startswith('#'):
                continue
            
            # Parse KEY=VALUE format
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                
                # Remove quotes if present
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                elif value.startswith("'") and value.endswith("'"):
                    value = value[1:-1]
                
                # Set environment variable
                os.environ[key] = value
    
    return True

# Load .env file
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    load_env_manually(env_path)
else:
    print("⚠️  No .env file found. Make sure environment variables are set manually.")

import uvicorn
from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from extraction import extract
    from config import settings
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Make sure all required environment variables are set.")
    sys.exit(1)


class ExtractionRequest(BaseModel):
    """Request model for document extraction."""
    path: str

    class Config:
        json_schema_extra = {
            "example": {
                "path": "documents/sample.pdf"
            }
        }


class HealthResponse(BaseModel):
    """Health check response model."""
    status: str
    service: str
    version: str


# Create FastAPI app
app = FastAPI(
    title="Document Extraction API",
    description="Local FastAPI server for testing AWS Lambda document extraction",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint providing basic service information."""
    return HealthResponse(
        status="healthy",
        service="Document Extraction API",
        version="1.0.0"
    )


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        service="Document Extraction API",
        version="1.0.0"
    )


@app.post("/extract")
async def extract_document(request: ExtractionRequest):
    """
    Extract text from a PDF document.
    
    Args:
        request: ExtractionRequest containing the document path
        
    Returns:
        JSON response with extraction results or error details
    """
    try:
        # Call the extraction function (same as Lambda handler)
        result = extract(request.path)
        
        # Convert the result to dict (same as Lambda handler)
        response_data = result.model_dump(mode='json')
        
        # Return appropriate HTTP status code based on success
        if response_data.get("success", False):
            return JSONResponse(
                content=response_data,
                status_code=200
            )
        else:
            # Return error with appropriate HTTP status code
            status_code = response_data.get("status_code", 500)
            return JSONResponse(
                content=response_data,
                status_code=status_code
            )
            
    except Exception as e:
        # Handle unexpected errors
        error_response = {
            "success": False,
            "error": str(e),
            "message": "An unexpected error occurred during extraction"
        }
        return JSONResponse(
            content=error_response,
            status_code=500
        )


@app.post("/extract-lambda")
async def extract_document_lambda_format(
    event: Dict[str, Any] = Body(..., example={"path": "documents/sample.pdf"})
):
    """
    Extract text from a PDF document using Lambda event format.
    
    This endpoint mimics the exact Lambda handler interface for compatibility testing.
    
    Args:
        event: Lambda event dict containing the document path
        
    Returns:
        JSON response with extraction results or error details
    """
    try:
        # Validate that the event has the required 'path' key
        if "path" not in event:
            raise HTTPException(
                status_code=400,
                detail="Event must contain 'path' key"
            )
        
        # Call the extraction function (same as Lambda handler)
        result = extract(event["path"])
        
        # Convert the result to dict (same as Lambda handler)
        response_data = result.model_dump()
        
        return JSONResponse(
            content=response_data,
            status_code=200
        )
        
    except HTTPException:
        raise
    except Exception as e:
        # Handle unexpected errors
        error_response = {
            "success": False,
            "error": str(e),
            "message": "An unexpected error occurred during extraction"
        }
        return JSONResponse(
            content=error_response,
            status_code=500
        )


@app.get("/config")
async def get_config():
    """
    Get current configuration (for debugging).
    
    Returns basic configuration info without sensitive data.
    """
    try:
        return {
            "aws_region": settings.AWS_REGION_NAME,
            "docs_bucket": settings.DOCS_S3_BUCKET_NAME,
            "extracted_bucket": settings.EXTRACTED_S3_BUCKET_NAME,
            "environment": os.environ.get("ENV", "not set"),
            "log_level": settings.get_log_level()
        }
    except Exception as e:
        return {
            "error": str(e),
            "message": "Could not load configuration. Check environment variables."
        }


def check_environment():
    """Check if all required environment variables are set."""
    required_vars = [
        "AWS_REGION_NAME",
        "AWS_S3_ACCESS_KEY_ID", 
        "AWS_S3_SECRET_ACCESS_KEY",
        "DOCS_S3_BUCKET_NAME",
        "EXTRACTED_S3_BUCKET_NAME"
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.environ.get(var)
        if not value:
            missing_vars.append(var)
        else:
            print(f"✅ {var}: {value[:10]}...")  # Show first 10 chars for verification
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"  - {var}")
        print("\nPlease set these environment variables before running the server.")
        print("You can create a .env file or export them in your shell.")
        print("\nCurrent environment variables:")
        for var in required_vars:
            value = os.environ.get(var, "NOT SET")
            print(f"  {var}={value}")
        return False
    
    print("✅ All required environment variables are set.")
    return True


def load_env_file():
    """Load environment variables from .env file."""
    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        print(f"📋 Loading environment variables from {env_path}")
        try:
            load_env_manually(env_path)
            print("✅ Environment variables loaded from .env file")
            return True
        except Exception as e:
            print(f"❌ Error loading .env file: {e}")
            return False
    else:
        print("⚠️  No .env file found. Make sure environment variables are set manually.")
        return False


if __name__ == "__main__":
    print("🚀 Starting Document Extraction API locally...")
    print("=" * 50)
    
    # Load environment variables from .env file
    load_env_file()
    
    # Check environment variables
    if not check_environment():
        sys.exit(1)
    
    # Set environment to local for appropriate logging
    os.environ["ENV"] = "local"
    
    print("📋 API Documentation:")
    print("  - Swagger UI: http://localhost:8000/docs")
    print("  - ReDoc: http://localhost:8000/redoc")
    print("  - Health Check: http://localhost:8000/health")
    print("  - Config Info: http://localhost:8000/config")
    print()
    print("🔧 API Endpoints:")
    print("  - POST /extract - Extract document (FastAPI format)")
    print("  - POST /extract-lambda - Extract document (Lambda format)")
    print()
    print("📝 Example request:")
    print('  curl -X POST "http://localhost:8000/extract" \\')
    print('    -H "Content-Type: application/json" \\')
    print('    -d \'{"path": "documents/sample.pdf"}\'')
    print()
    print("🛑 Press Ctrl+C to stop the server")
    print("=" * 50)
    
    # Start the server
    uvicorn.run(
        "run_locally:app",
        host="0.0.0.0",
        port=8000,
        log_level="info",
        reload=True,  # Enable auto-reload for development
        reload_dirs=["src"]  # Watch src directory for changes
    )
