# Running Locally

This document explains how to run the document extraction API locally for development and testing.

## Prerequisites

1. Python 3.8 or higher
2. AWS credentials with access to the configured S3 buckets
3. All dependencies installed (see Installation section)

## Installation

1. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up environment variables:
   ```bash
   # Copy the example environment file
   cp .env.example .env
   
   # Edit .env with your actual AWS credentials and bucket names
   # Required variables:
   # - AWS_REGION_NAME
   # - AWS_S3_ACCESS_KEY_ID
   # - AWS_S3_SECRET_ACCESS_KEY
   # - DOCS_S3_BUCKET_NAME
   # - EXTRACTED_S3_BUCKET_NAME
   ```

3. Alternatively, you can export environment variables directly:
   ```bash
   export ENV=local
   export AWS_REGION_NAME=us-east-1
   export AWS_S3_ACCESS_KEY_ID=your_access_key
   export AWS_S3_SECRET_ACCESS_KEY=your_secret_key
   export DOCS_S3_BUCKET_NAME=your-docs-bucket
   export EXTRACTED_S3_BUCKET_NAME=your-extracted-bucket
   ```

## Running the Server

Start the local development server:

```bash
python run_locally.py
```

The server will start on `http://localhost:8000` with the following features:

- **Auto-reload**: The server automatically restarts when you make changes to the code
- **Interactive API docs**: Available at `http://localhost:8000/docs`
- **Alternative docs**: Available at `http://localhost:8000/redoc`

## API Endpoints

### Health Check
```bash
GET http://localhost:8000/health
```

### Extract Document (FastAPI format)
```bash
POST http://localhost:8000/extract
Content-Type: application/json

{
  "path": "documents/sample.pdf"
}
```

### Extract Document (Lambda format)
```bash
POST http://localhost:8000/extract-lambda
Content-Type: application/json

{
  "path": "documents/sample.pdf"
}
```

### Configuration Info
```bash
GET http://localhost:8000/config
```

## Example Usage

Using curl:
```bash
# Health check
curl http://localhost:8000/health

# Extract document
curl -X POST "http://localhost:8000/extract" \
  -H "Content-Type: application/json" \
  -d '{"path": "documents/sample.pdf"}'

# Extract using Lambda format (for testing compatibility)
curl -X POST "http://localhost:8000/extract-lambda" \
  -H "Content-Type: application/json" \
  -d '{"path": "documents/sample.pdf"}'
```

Using Python requests:
```python
import requests

# Health check
response = requests.get("http://localhost:8000/health")
print(response.json())

# Extract document
response = requests.post(
    "http://localhost:8000/extract",
    json={"path": "documents/sample.pdf"}
)
print(response.json())
```

## Response Format

### Successful Extraction
```json
{
  "success": true,
  "docHash": "sha256hash...",
  "key": "path/to/extracted/content.json",
  "docType": "text_based"
}
```

### Error Response
```json
{
  "success": false,
  "timestamp": "2025-07-03T10:30:00Z",
  "originatingSystem": "foss-api",
  "environment": "local",
  "logLevel": "ERROR",
  "path": "documents/sample.pdf",
  "statusCode": 404,
  "message": "File not found",
  "stackTrace": "..."
}
```

## Troubleshooting

### Environment Variables Not Set
If you see an error about missing environment variables, make sure all required variables are set:
- `AWS_REGION_NAME`
- `AWS_S3_ACCESS_KEY_ID`
- `AWS_S3_SECRET_ACCESS_KEY`
- `DOCS_S3_BUCKET_NAME`
- `EXTRACTED_S3_BUCKET_NAME`

### AWS Credentials
Make sure your AWS credentials have the necessary permissions:
- Read access to the `DOCS_S3_BUCKET_NAME` bucket
- Write access to the `EXTRACTED_S3_BUCKET_NAME` bucket

### Import Errors
If you encounter import errors, make sure all dependencies are installed:
```bash
pip install -r requirements.txt
```

### File Not Found Errors
The `path` parameter should be the S3 key (path) of the document in your `DOCS_S3_BUCKET_NAME`, not a local file path.

## Development

The server runs with auto-reload enabled, so any changes to files in the `src/` directory will automatically restart the server.

For debugging, you can:
1. Check the configuration endpoint: `http://localhost:8000/config`
2. View detailed logs in the terminal where you started the server
3. Use the interactive API documentation at `http://localhost:8000/docs`
