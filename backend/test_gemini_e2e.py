import requests
import sys

def test_gemini_endpoint():
    url = "http://localhost:8001/api/chat"
    payload = {
        "message": "Hello, are you working?",
        "model_type": "fast"
    }
    
    try:
        print(f"Sending request to {url}...")
        response = requests.post(url, json=payload)
        response.raise_for_status()
        
        data = response.json()
        print("Response received:")
        print(data)
        
        if "response" in data and data["response"]:
            print("SUCCESS: Received a valid response from Gemini Service.")
            return True
        else:
            print("FAILURE: Response did not contain expected data.")
            return False
            
    except Exception as e:
        print(f"FAILURE: An error occurred: {e}")
        return False

if __name__ == "__main__":
    success = test_gemini_endpoint()
    if not success:
        sys.exit(1)
