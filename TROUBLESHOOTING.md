# TikTok API Workflow Troubleshooting Guide

## Issues Fixed

### 1. Port Mismatch ❌➡️✅
- **Problem**: n8n workflow was trying to connect to `localhost:8080`
- **Solution**: Updated workflow to use `localhost:5000` (correct port from docker-compose.yml)

### 2. Endpoint Mismatch ❌➡️✅
- **Problem**: Workflow called `/api/download` endpoint
- **Solution**: Updated workflow to use `/extract_tiktok` endpoint (matches Flask API)

### 3. Request Format Mismatch ❌➡️✅
- **Problem**: Workflow sent `{"url": "...", "version": "v1"}` 
- **Solution**: Updated to send `{"url": "..."}` (matches API expectations)

### 4. Response Data Extraction ❌➡️✅
- **Problem**: Workflow expected different JSON structure
- **Solution**: Updated data extraction paths to match API response format

## How to Start the API Server

### Option 1: Using the startup script
```bash
./start_api.sh
```

### Option 2: Manual Docker commands
```bash
# Build and start the server
docker-compose up -d

# Check if it's running
docker-compose ps

# View logs
docker-compose logs -f
```

### Option 3: Direct Python execution
```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
python app.py
```

## Testing the API

### Test with curl:
```bash
curl -X POST http://localhost:5000/extract_tiktok \
  -H "Content-Type: application/json" \
  -d '{"url":"https://vt.tiktok.com/ZSDGDKF3r/"}'
```

### Test with Python script:
```bash
python test_api.py
```

## Common Issues & Solutions

### 1. "Connection Refused" Error
- **Cause**: API server not running
- **Solution**: Start the server using one of the methods above

### 2. "Bad Request" Error
- **Cause**: Wrong endpoint or malformed JSON
- **Solution**: Use `/extract_tiktok` endpoint with `{"url": "..."}` format

### 3. "Not Found" Error
- **Cause**: Wrong port or endpoint
- **Solution**: Ensure using `localhost:5000/extract_tiktok`

### 4. Workflow Still Failing
- **Cause**: n8n workflow not updated
- **Solution**: Import the updated `accurate_local_tiktok_workflow.json` into n8n

## API Endpoints

| Method | Endpoint | Description | Request Body |
|--------|----------|-------------|--------------|
| GET | `/` | API documentation | - |
| GET | `/health` | Health check | - |
| POST | `/extract_tiktok` | Extract video info | `{"url": "tiktok_url"}` |

## Response Format

```json
{
  "success": true,
  "data": {
    "id": "video_id",
    "title": "video_title",
    "desc": "video_description",
    "author": {
      "unique_id": "username",
      "nickname": "display_name"
    },
    "video": {
      "play_addr": "video_url",
      "download_addr": "download_url"
    },
    "play": "direct_video_url"
  }
}
```

## Monitoring

### Check server status:
```bash
curl http://localhost:5000/health
```

### View server logs:
```bash
docker-compose logs -f tiktok-api
```

### Stop the server:
```bash
docker-compose down
```