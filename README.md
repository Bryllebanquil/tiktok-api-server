# TikTok API Server

A Flask-based API server for extracting TikTok video information using the TikTokApi library.

## Features

- Extract TikTok video metadata (title, description, author, stats)
- Get video download URLs
- Extract hashtags from video descriptions
- Health check endpoint
- Docker support with Playwright browser automation
- Async/await support for better performance

## API Endpoints

### POST /extract_tiktok
Extract TikTok video information from a URL.

**Request Body:**
```json
{
  "url": "https://www.tiktok.com/@username/video/1234567890"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "video_id",
    "title": "Video title",
    "desc": "Video description",
    "author": {
      "unique_id": "username",
      "nickname": "Display Name",
      "avatar": "avatar_url"
    },
    "video": {
      "play_addr": "video_url",
      "download_addr": "download_url",
      "cover": "cover_image_url",
      "width": 720,
      "height": 1280,
      "duration": 15
    },
    "music": {
      "title": "Music title",
      "author": "Music author"
    },
    "stats": {
      "digg_count": 1000,
      "share_count": 100,
      "comment_count": 50,
      "play_count": 10000
    },
    "hashtags": "#fyp #viral",
    "play": "direct_video_url"
  }
}
```

### GET /health
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "TikTok API Extractor"
}
```

### GET /
API documentation and service information.

## Local Development

### Prerequisites
- Python 3.9+
- Docker (optional)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd tiktok-api
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install Playwright browsers:
```bash
playwright install chromium
```

4. Run the application:
```bash
python app.py
```

The server will start on `http://localhost:5000`.

### Docker Development

1. Build and run with Docker Compose:
```bash
docker-compose up --build
```

2. Or build and run with Docker:
```bash
docker build -t tiktok-api .
docker run -p 5000:5000 tiktok-api
```

## Deployment

### Render Deployment

1. Connect your GitHub repository to Render
2. Create a new Web Service
3. Configure the following settings:
   - **Build Command:** `pip install -r requirements.txt && playwright install chromium`
   - **Start Command:** `gunicorn --bind 0.0.0.0:$PORT --workers 1 --timeout 120 app:app`
   - **Environment:** Python 3.9
   - **Plan:** Starter (free) or higher

### Environment Variables

- `PORT`: Server port (default: 5000)
- `DEBUG`: Debug mode (default: false)

## Usage Examples

### Using curl:
```bash
# Extract TikTok video
curl -X POST http://localhost:5000/extract_tiktok \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.tiktok.com/@username/video/1234567890"}'

# Health check
curl http://localhost:5000/health
```

### Using Python requests:
```python
import requests

# Extract TikTok video
response = requests.post('http://localhost:5000/extract_tiktok', 
                        json={'url': 'https://www.tiktok.com/@username/video/1234567890'})
data = response.json()
print(data)
```

## Supported URL Formats

- `https://www.tiktok.com/@username/video/1234567890`
- `https://vm.tiktok.com/ABC123`
- `https://tiktok.com/@username/video/1234567890`

## Error Handling

The API returns appropriate HTTP status codes:
- `200`: Success
- `400`: Bad Request (invalid URL or missing parameters)
- `500`: Internal Server Error

## License

MIT License
