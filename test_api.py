#!/usr/bin/env python3
"""
Test script for the TikTok API server
"""
import requests
import json

def test_api():
    """Test the TikTok API server"""
    url = "http://localhost:5000/extract_tiktok"
    test_data = {
        "url": "https://vt.tiktok.com/ZSDGDKF3r/"
    }
    
    try:
        print("Testing TikTok API server...")
        print(f"URL: {url}")
        print(f"Data: {json.dumps(test_data, indent=2)}")
        
        response = requests.post(url, json=test_data, timeout=30)
        
        print(f"\nResponse Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ Success! Response:")
            print(json.dumps(result, indent=2))
        else:
            print(f"\n❌ Error! Response:")
            print(response.text)
            
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Connection Error: {e}")
        print("Make sure the API server is running on localhost:5000")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_api()