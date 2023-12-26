import requests
import os

# url = "http://127.0.0.1:8005/upload/"
# url = "http://192.168.0.68:13390/upload/"
url = "http://113.198.63.26:13392/upload/"

image_directory = 'images'
image_files = [os.path.join(image_directory, file) for file in os.listdir(image_directory) if file.endswith('.jpg')]
files = [('files', (open(file, 'rb'))) for file in image_files]

response = requests.post(url, files=files)

print(response.text)