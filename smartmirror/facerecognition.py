import time

import cv2

CAM_ID = 0


def face_recognition(running_flag, recognized_face):
    """Performs face detection and recognition.

    This function is supposed to be invoked as a callback for separate
    process.

    Args:
        running_flag: multiprocessing.Event flag controlling the while
            loop. When set to false this function will exit the loop
            and clean up before finishing.
        recognized_face: multiprocessing.Value(ctypes.c_int) variable
            for storing id of recognized face.
            This variable is set to -1 if face was not detected, 0 if
            face was detected but not recognized or id if face was
            detected and recognized.

    Raises:
        ValueError: if either camera was not detected or cascade file
            was not found.
    """
    camera = cv2.VideoCapture()
    camera.open(CAM_ID)
    if not camera.isOpened():
        raise ValueError('Camera not found')

    face_cascade_classifier = cv2.CascadeClassifier('../resources/haarcascade_frontalface_alt2.xml')
    if face_cascade_classifier.empty():
        raise ValueError('haarcascade_frontalface_alt2.xml not found')

    face_recognizer = cv2.face.LBPHFaceRecognizer_create()
    try:
        face_recognizer.read('../resources/face_recognition_data.yml')
    except cv2.error:
        face_recognizer.write('../resources/face_recognition_data.yml')
    # This loop should run as long as the main window is open.
    while running_flag.is_set():

        ret, img = camera.read()
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        detected_faces_tuple = face_cascade_classifier.detectMultiScale(img)
        # If any face was detected.
        if len(detected_faces_tuple) > 0:

            # Cropping image to detected face region. Picking first
            # face from the list gives us the biggest one (due to the
            # way that Haar Cascade works), which we assume is the
            # face we're interested in.
            x, y, w, h = detected_faces_tuple[0]
            face_img = img[y: y + h, x: x + w]

            try:
                label, confidence = face_recognizer.predict(face_img)
                if confidence < 60:
                    recognized_face.value = label
                else:
                    recognized_face.value = 0
            except cv2.error:
                # This will occur if recognizer was never trained.
                recognized_face.value = 0
        else:
            recognized_face.value = -1

        time.sleep(0.2)

    camera.release()
