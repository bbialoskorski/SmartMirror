import os
from PIL import Image

import numpy as np
import cv2

TRAINING_DATA_PATH = '../resources/training_data/'


def train_recognizer(user_id):
    """Loads training data from disk and trains face recognizer.

    Args:
        user_id: integer to be used as a training label. This is the
            number that will be returned by recognizer.

    Raises:
         ValueError: if yml file containing recognizer data was not
            found.
    """

    face_recognizer = cv2.face.LBPHFaceRecognizer_create()
    try:
        face_recognizer.read('../resources/face_recognition_data.yml')
    except cv2.error:
        face_recognizer.write('../resources/face_recognition_data.yml')
    face_images = list()
    face_labels = list()

    for file in os.listdir(TRAINING_DATA_PATH):

        image_path = os.path.join(TRAINING_DATA_PATH, file)
        face_img = Image.open(image_path).convert('L')
        face_image_np = np.array(face_img, 'uint8')
        face_images.append(face_image_np)
        face_labels.append(user_id)

    face_recognizer.update(face_images, np.array(face_labels))
    face_recognizer.write('../resources/face_recognition_data.yml')
