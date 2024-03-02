import requests

# Replace this URL with the actual URL where your Flask app is running
api_url = "http://127.0.0.1:5000/upload/"
# api_url = 'http://137.184.226.218:5000/process_video'

# Replace this file path with the path to your test video file
video_file_path = "data/d.mp4"

# Create a dictionary with the file to be sent in the request
files = {'file': open(video_file_path, 'rb')}

# Send a POST request to the API
try:
    response = requests.post(api_url, files=files, timeout=80)  # Timeout in seconds
    print(response.status_code)
    print(response.json())
except requests.exceptions.RequestException as e:
    print(f"Error: {e}")

# Print the response from the API
# print(response.json())
