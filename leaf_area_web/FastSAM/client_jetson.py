import serial
import requests
import os
import cv2
from datetime import datetime

url = "http://113.198.63.26:13392/upload/"
ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)

capture_counter = 0
def gstreamer_pipeline():
    return (
        "nvarguscamerasrc ! "
        "video/x-raw(memory:NVMM), width=(int)1280, height=(int)1080, format=(string)NV12, framerate=(fraction)30/1 ! "
        "nvvidconv ! video/x-raw, format=(string)BGRx ! "
        "videoconvert ! video/x-raw, format=(string)BGR ! appsink"
    )

def capture_image(filename):
    if not os.path.exists('capture_images'):
        os.makedirs('capture_images')

    full_filename = os.path.join('capture_images', filename)
    cap = cv2.VideoCapture(gstreamer_pipeline(), cv2.CAP_GSTREAMER)
    if cap.isOpened():
        ret, frame = cap.read()
        if ret:
            cv2.imwrite(full_filename, frame)
        cap.release()
    else:
        print("Unable to open the camera")

if __name__=='__main__':
    while True:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').rstrip()

            if line == "CAPTURE":
                now = datetime.now()
                filename = f"image_{now.strftime('%Y%m%d_%H%M')}_{capture_counter}.jpg"  # 파일명에 카운터 추가
                capture_image(filename)
                capture_counter += 1

            elif line == "SEND":
                image_files = [os.path.join('capture_images', file) for file in os.listdir('capture_images') if file.endswith('.jpg') or file.endswith('.png')]
                files = [('files', (open(file, 'rb'))) for file in image_files]

                response = requests.post(url, files=files)
                print(response.text)

                for file in image_files:
                    os.remove(file)
                break

