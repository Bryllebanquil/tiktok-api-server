from flask import Flask, request, jsonify
import requests
import re
import os
import logging
import json

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

def extract_video_id_from_url(url):
    """Extract video ID from TikTok URL"""
    patterns = [
        r'/@[\w\.-]+/video/(\d+)',
        r'/video/(\d+)',
        r'v/(\d+)',
        r'tiktok\.com/.*?/(\d+)',
        r'vm\.tiktok\.com/(\w+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def extract_hashtags(text):
    """Extract hashtags from text"""
    if not text:
        return ""
    hashtag_pattern = r'#[\w\u4e00-\u9fff]+'
    hashtags = re.findall(hashtag_pattern, text)
    return ' '.join(hashtags)

def get_video_data(url):
    """Get video data from TikTok URL using direct HTTP requests"""
    try:
        video_id = extract_video_id_from_url(url)
        if not video_id:
            return {"error": "Invalid TikTok URL"}

        # Headers to mimic a browser request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }

        # Make request to TikTok URL
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code != 200:
            return {"error": "Failed to fetch TikTok page"}

        # Extract JSON data from the page
        html_content = response.text
        
        # Look for JSON data in script tags (updated for SIGI_STATE)
        json_pattern = r"window\['SIGI_STATE'\]\s*=\s*({.*?});"  # New TikTok state var
        match = re.search(json_pattern, html_content, re.DOTALL)
        if not match:
            # Try alternative pattern (sometimes just SIGI_STATE)
            json_pattern = r'SIGI_STATE\s*=\s*({.*?});'
            match = re.search(json_pattern, html_content, re.DOTALL)
        if not match:
            return {"error": "Could not extract video data from TikTok page"}
        try:
            data = json.loads(match.group(1))
        except json.JSONDecodeError:
            return {"error": "Invalid JSON data in TikTok page"}

        # Extract video information from the JSON data
        # This is a simplified extraction - the actual structure may vary
        video_data = data.get('VideoModule', {}).get('videoData', {})
        
        if not video_data:
            return {"error": "Video data not found in TikTok page"}

        # Extract relevant information
        result = {
            "success": True,
            "data": {
                "id": video_data.get("id", ""),
                "title": video_data.get("desc", ""),
                "desc": video_data.get("desc", ""),
                "create_time": video_data.get("createTime", 0),
                "author": {
                    "unique_id": video_data.get("author", {}).get("uniqueId", ""),
                    "nickname": video_data.get("author", {}).get("nickname", ""),
                    "avatar": video_data.get("author", {}).get("avatarMedium", "")
                },
                "video": {
                    "play_addr": video_data.get("video", {}).get("playAddr", ""),
                    "download_addr": video_data.get("video", {}).get("downloadAddr", ""),
                    "cover": video_data.get("video", {}).get("cover", ""),
                    "dynamic_cover": video_data.get("video", {}).get("dynamicCover", ""),
                    "width": video_data.get("video", {}).get("width", 0),
                    "height": video_data.get("video", {}).get("height", 0),
                    "duration": video_data.get("video", {}).get("duration", 0)
                },
                "music": {
                    "id": video_data.get("music", {}).get("id", ""),
                    "title": video_data.get("music", {}).get("title", ""),
                    "author": video_data.get("music", {}).get("authorName", ""),
                    "play_url": video_data.get("music", {}).get("playUrl", "")
                },
                "stats": {
                    "digg_count": video_data.get("stats", {}).get("diggCount", 0),
                    "share_count": video_data.get("stats", {}).get("shareCount", 0),
                    "comment_count": video_data.get("stats", {}).get("commentCount", 0),
                    "play_count": video_data.get("stats", {}).get("playCount", 0)
                },
                "hashtags": extract_hashtags(video_data.get("desc", "")),
                "play": video_data.get("video", {}).get("downloadAddr", "") or video_data.get("video", {}).get("playAddr", "")
            }
        }
        
        return result
        
    except Exception as e:
        logger.error(f"Error extracting video data: {str(e)}")
        return {"error": f"Failed to extract video data: {str(e)}"}

@app.route('/extract_tiktok', methods=['POST'])
def extract_tiktok():
    """Extract TikTok video information"""
    try:
        data = request.get_json()
        if not data or 'url' not in data:
            return jsonify({"error": "URL is required"}), 400
        
        url = data['url']
        
        # Validate URL
        if 'tiktok.com' not in url:
            return jsonify({"error": "Invalid TikTok URL"}), 400
        
        # Get video data
        result = get_video_data(url)
        
        if "error" in result:
            return jsonify(result), 400
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in extract_tiktok: {str(e)}")
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "TikTok API Extractor"})

@app.route('/', methods=['GET'])
def home():
    """Home endpoint with API documentation"""
    return jsonify({
        "service": "TikTok API Extractor",
        "version": "1.0.0",
        "endpoints": {
            "/extract_tiktok": {
                "method": "POST",
                "description": "Extract TikTok video information",
                "body": {
                    "url": "TikTok video URL"
                },
                "response": {
                    "success": "boolean",
                    "data": {
                        "id": "video ID",
                        "title": "video title/description",
                        "desc": "video description",
                        "author": "author information",
                        "video": "video URLs and metadata",
                        "music": "music information",
                        "stats": "video statistics",
                        "hashtags": "extracted hashtags",
                        "play": "direct video URL for download"
                    }
                }
            },
            "/health": {
                "method": "GET",
                "description": "Health check endpoint"
            }
        }
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)