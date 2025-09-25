from flask import Flask, request, jsonify
from TikTokApi import TikTokApi
import asyncio
import re
import os
import logging

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

async def get_video_data(url):
    """Get video data from TikTok URL"""
    try:
        video_id = extract_video_id_from_url(url)
        if not video_id:
            return {"error": "Invalid TikTok URL"}

        # Initialize TikTok API
        async with TikTokApi() as api:
            # Get video data using the new API
            video = await api.video(url=url).info()
            
            if not video:
                return {"error": "Video not found or private"}
            
            # Extract relevant information
            result = {
                "success": True,
                "data": {
                    "id": video.get("id", ""),
                    "title": video.get("desc", ""),
                    "desc": video.get("desc", ""),
                    "create_time": video.get("createTime", 0),
                    "author": {
                        "unique_id": video.get("author", {}).get("uniqueId", ""),
                        "nickname": video.get("author", {}).get("nickname", ""),
                        "avatar": video.get("author", {}).get("avatarMedium", "")
                    },
                    "video": {
                        "play_addr": video.get("video", {}).get("playAddr", ""),
                        "download_addr": video.get("video", {}).get("downloadAddr", ""),
                        "cover": video.get("video", {}).get("cover", ""),
                        "dynamic_cover": video.get("video", {}).get("dynamicCover", ""),
                        "width": video.get("video", {}).get("width", 0),
                        "height": video.get("video", {}).get("height", 0),
                        "duration": video.get("video", {}).get("duration", 0)
                    },
                    "music": {
                        "id": video.get("music", {}).get("id", ""),
                        "title": video.get("music", {}).get("title", ""),
                        "author": video.get("music", {}).get("authorName", ""),
                        "play_url": video.get("music", {}).get("playUrl", "")
                    },
                    "stats": {
                        "digg_count": video.get("stats", {}).get("diggCount", 0),
                        "share_count": video.get("stats", {}).get("shareCount", 0),
                        "comment_count": video.get("stats", {}).get("commentCount", 0),
                        "play_count": video.get("stats", {}).get("playCount", 0)
                    },
                    "hashtags": extract_hashtags(video.get("desc", "")),
                    "play": video.get("video", {}).get("downloadAddr", "") or video.get("video", {}).get("playAddr", "")
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
        
        # Run async function
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(get_video_data(url))
        loop.close()
        
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