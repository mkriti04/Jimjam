import cv2
import time
import numpy as np
import matplotlib.pyplot as plt
import requests

# ThingSpeak parameters
API_KEY = 'VBW8G1SZZK98R4HF'  # Replace with your ThingSpeak API Key
CHANNEL_ID = '2267674'  # Replace with your ThingSpeak Channel ID
FIELD_ID = 1  # Field 1 for radius

# Create a VideoCapture object
cap = cv2.VideoCapture(0)
print("started")
# Define the codec and create a VideoWriter object
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter('output.avi', fourcc, 20.0, (640, 480))

# Initialize the arrays to store data
times = []
radii = []

# Capture the video for 10 seconds and store the frames in an array
frames = []
while len(frames) <= 300:
    ret, frame = cap.read()
    frames.append(frame)
    # Release the resources
cap.release()

# Get the start time
start_time = time.time()

# Process the frames and store the radii in an array
for i in range(len(frames)):
    frame = frames[i]
    # Convert the image to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Apply Gaussian blur to reduce noise
    gray_blur = cv2.GaussianBlur(gray, (5, 5), 0)

    # Detect the eye region using a cascade classifier
    eye_cascade = cv2.CascadeClassifier('./haarcascade_eye.xml')
    eyes = eye_cascade.detectMultiScale(gray_blur, 1.3, 5)

    if len(eyes) == 0:
        continue

    # Get the eye region and calculate the radius of the pupil
    for (ex, ey, ew, eh) in eyes:
        eye_roi = gray_blur[ey:ey+eh, ex:ex+ew]

        # Apply thresholding to separate the pupil from the iris
        _, threshold = cv2.threshold(eye_roi, 40, 255, cv2.THRESH_BINARY_INV)
        
        # Find the contours of the thresholded image
        contours, _ = cv2.findContours(threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        # Find the contour with the largest area, which corresponds to the pupil
        if len(contours) > 0:
            pupil_contour = max(contours, key=cv2.contourArea)
            
            # Calculate the radius of the pupil
            radius = int(cv2.minEnclosingCircle(pupil_contour)[1])

            # Append the current time and radius to the arrays
            current_time = time.time() - start_time
            times.append(current_time)
            radii.append(radius)

            # Draw the circle around the pupil on the original image
            cv2.circle(frame, (ex+int(pupil_contour[:, 0, 0].mean()), ey+int(pupil_contour[:, 0, 1].mean())), radius, (0, 255, 0), 2)

            # Send data to ThingSpeak
            if len(times) % 10 == 0:  # Send data every 10 frames
                radius_data = str(radius)
                # time_data = str(current_time)
                url = f'https://api.thingspeak.com/update?api_key={API_KEY}&field{FIELD_ID}={radius_data}'
                response = requests.get(url)
                if response.status_code == 200:
                    print('Data sent to ThingSpeak successfully')

    # Write the frame to the output video
    out.write(frame)

# take only one value for 10 consecutive values in radii for graph
radii1 = [radii[i] for i in range(len(radii)) if i % 10 == 0]
times1 = [times[i] for i in range(len(times)) if i % 10 == 0]

plt.plot(times1, radii1)
plt.xlabel('Time (s)')
plt.ylabel('Radius')
plt.show()
