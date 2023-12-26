import cv2
import os
import numpy as np
from plantcv import plantcv as pcv
import time
from datetime import datetime
import serial
import pandas as pd

now = datetime.now()
ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
time.sleep(2)

def gstreamer_pipeline():
    return (
        "nvarguscamerasrc ! "
        "video/x-raw(memory:NVMM), width=(int)1280, height=(int)1080, format=(string)NV12, framerate=(fraction)30/1 ! "
        "nvvidconv ! video/x-raw, format=(string)BGRx ! "
        "videoconvert ! video/x-raw, format=(string)BGR ! appsink"
    )

def capture_image(filename):
    if not os.path.exists('capture_images'):  # Check if the folder exists
        os.makedirs('capture_images')  # Create the folder if it doesn't exist

    full_filename = os.path.join('capture_images', filename)
    cap = cv2.VideoCapture(gstreamer_pipeline(), cv2.CAP_GSTREAMER)
    if cap.isOpened():
        ret, frame = cap.read()
        if ret:
            cv2.imwrite(full_filename, frame)  # Save in 'capture_images' folder
        cap.release()
    else:
        print("Unable to open the camera")

def process_image(filename):
    if not os.path.exists('processed_images'):
        os.makedirs('processed_images')

    img, path, _ = pcv.readimage(filename=os.path.join('capture_images', filename))

    s = pcv.rgb2gray_hsv(rgb_img=img, channel='s')
    s_thresh = pcv.threshold.binary(gray_img=s, threshold=80, object_type='light')
    s_mblur = pcv.median_blur(gray_img=s_thresh, ksize=3)

    b = pcv.rgb2gray_lab(rgb_img=img, channel='b')
    b_thresh = pcv.threshold.binary(gray_img=b, threshold=144, object_type='light')

    # pcv.plot_image(b_thresh)
    # mask_pixel_count = cv2.countNonZero(s_mblur)
    mask_pixel_count = cv2.countNonZero(b_thresh)
    processed_filename = os.path.join('processed_images', f'{filename[:-4]}_processed.jpg')
    cv2.imwrite(processed_filename, b_thresh)  # Save in 'processed_images' folder

    actual_leaf_area = mask_pixel_count * 0.000508
    actual_leaf_area = round(actual_leaf_area, 2)
    #print(mask_pixel_count)
    print("Actual leaf area: ", actual_leaf_area, 'cm^2')

    ser.write(str(actual_leaf_area).encode())

    return actual_leaf_area

def main():
    # results = []  # List to store leaf area results
    # while True:
    #     user_input = input("Capture image and calculate area? (yes/no): ")
    #     if user_input.lower() == 'yes':
    #         filename = "csi_camera_image.jpg"
    #         capture_image(filename)
    #         leaf_area = process_image(filename)
    #         results.append(leaf_area)  # Add the result to the list
    #     elif user_input.lower() == 'no':
    #         break
    #
    # df = pd.DataFrame({'Leaf_Area': results})
    # df.to_csv('results.csv', index=False)
    # print("Results saved to 'results.csv'")
    # print("Exiting program.")

    results = []
    image_count = 0
    while True:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').rstrip()
            if line == "YES":
                image_count += 1
                filename = f"csi_camera_image_{image_count}.jpg"
                capture_image(filename)
                results.append({'Filename': filename, 'Leaf_Area': process_image(filename)})
            elif line == "NO":
                break  # Exit the loop if 'NO' is received

    # Save the results to a CSV file
    df = pd.DataFrame(results)
    df.to_csv(f'{datetime.now().strftime("%Y%m%d")}_results.csv', index=False)
    print("Results saved to 'results.csv'")
    print("Exiting program.")

if __name__ == "__main__":
    main()
