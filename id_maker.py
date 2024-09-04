import cv2
import re
import os
import numpy as np
from tkinter import Tk, Button, Label, filedialog, Entry
from PIL import Image, ImageDraw, ImageFont

modelFile = "res10_300x300_ssd_iter_140000.caffemodel"
configFile = "deploy.prototxt"

output_path = r"ID-MAKER\IDs"

def detect_face_dnn(image_path):
    # Load the DNN model
    net = cv2.dnn.readNetFromCaffe(configFile, modelFile)

    # Read the image
    image = cv2.imread(image_path)
    if image is None:
        print("Error: Image not found")
        return None

    (h, w) = image.shape[:2]

    # Create blob from image
    blob = cv2.dnn.blobFromImage(cv2.resize(image, (300, 300)), 1.0, (300, 300), (104.0, 177.0, 123.0))

    # Set the blob as input to the network
    net.setInput(blob)

    # Perform inference and get the faces
    detections = net.forward()

    # Find the face with the highest confidence
    max_confidence = 0
    face = None

    for i in range(0, detections.shape[2]):
        confidence = detections[0, 0, i, 2]

        # Ensure the confidence is above a threshold
        if confidence > 0.5 and confidence > max_confidence:
            max_confidence = confidence
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            (startX, startY, endX, endY) = box.astype("int")

            padding = 100  # You can adjust this value
            startX = max(0, startX - padding)
            startY = max(0, startY - padding)
            endX = min(w, endX + padding)
            endY = min(h, endY + padding)

            # Extract the face
            face = image[startY:endY, startX:endX]

    return face

def create_id_card(face_image, name, save_path):
    id_template = Image.open("ID Card.png")

    # Convert the face image from OpenCV format to PIL format
    image = Image.fromarray(cv2.cvtColor(face_image, cv2.COLOR_BGR2RGB))

    # Resize the image using LANCZOS resampling (formerly known as ANTIALIAS)
    face_pil = image.resize((290, 290), Image.Resampling.LANCZOS)

    #(290, 290) is the size of the image panel
    #starting point: (155, 250) end point: (435, 530) | w = 435 - 155 h = 530 - 250

    # Paste the face onto the ID template
    id_template.paste(face_pil, (150, 245, 440, 535))

    # (150, 245, 440, 535) is the starting point and endpoint of the image panel of the template

    # Import the font
    font = ImageFont.truetype('glacial-indifference.bold.otf', size=23)
    draw = ImageDraw.Draw(id_template)

    # Calculate the bounding box of the text
    text_bbox = draw.textbbox((0, 0), name, font=font)

    # Calculate the width of the text
    text_width = text_bbox[2] - text_bbox[0]

    # Calculate the x-coordinate to center the text
    x_position = (id_template.width - text_width) // 2

    # Draw the text centered
    draw.text((x_position, 706), name, font=font, fill='#04294f')

    # x_position is the calculated center of the bounding box, 706 is the y_position

    # Display the finished ID card
    id_template.show()

    # Save the finished ID card
    id_template.save(save_path)

def upload_image():
    file_path = filedialog.askopenfilename()
    face_image = detect_face_dnn(file_path)
    if face_image is not None:
        name = name_entry.get()
        file_name = f"{filename(name)}_id_card.png"
        save_path = os.path.join(output_path, file_name)
        create_id_card(face_image, name.title(), save_path)
    else:
        print("No face detected or image not found.")

def filename(s):

    # Remove all non-word characters (everything except numbers and letters)
    s = re.sub(r"[^\w\s]", '', s)

    # Replace all runs of whitespace with a single dash
    s = re.sub(r"\s+", '_', s)

    return s.lower()

# Initialize Tkinter GUI
root = Tk()
root.title("ID Card Generator")

# Name entry
Label(root, text="Enter your name:").pack(pady=10)
name_entry = Entry(root, width=30)
name_entry.pack(pady=5)

# Upload button
upload_button = Button(root, text="Upload Image", command=upload_image)
upload_button.pack(pady=20)

# Quit button
quit_button = Button(root, text="Quit", command=root.quit)
quit_button.pack(pady=10)

root.mainloop()
