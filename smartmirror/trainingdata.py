import os
import multiprocessing

import cv2

CAM_ID = 0

TRAINING_DATA_PATH = '../resources/training_data/'


class TrainingData:
    """Asynchronously collects training data for face recognizer.

    TrainingData uses multiprocessing module to asynchronously collect
    data meant for training of opencv's face recognition algorithms.
    Mentioned data is in the form of grayscale pictures containing
    only facial region.
    Only one 'collector' can be run at the same time.
    """
    def __init__(self):

        self._running_flag = multiprocessing.Event()
        self._data_collector_process = multiprocessing.Process(target=collect_data,
                                                               daemon=True,
                                                               args=(self._running_flag,))

    def collect_data(self):
        """Starts collecting training data.

        Only one 'collector' can be run at the same time.

        Returns:
            0 if TrainingData successfully started collecting data or
            1 if training data is already being collected.
        """
        if self._data_collector_process.is_alive():

            return 1

        else:
            try:
                self._running_flag.set()
                self._data_collector_process.start()
            except AssertionError:
                # This exception means that our process was already
                # started and finished execution so we join it and
                # then create and start a new one.
                self._data_collector_process.join()
                self._data_collector_process = multiprocessing.Process(target=collect_data,
                                                                       daemon=True,
                                                                       args=(self._running_flag,))
                self._running_flag.set()
                self._data_collector_process.start()

            return 0

    def is_running(self):
        """Checks whether data is being collected.

        Returns:
             bool value
        """
        return self._data_collector_process.is_alive()

    def stop_collector(self):
        """Stops data collection process.

        This function stops collector process.
        Even if process was not running this function will attempt to
        join it.

        Returns:
            0 if process was running and successfully stopped or -1 if
            process was not running.
        """
        if self._data_collector_process.is_alive():
            self._running_flag.clear()
            self._data_collector_process.join()
            return 0
        else:
            try:
                self._data_collector_process.join()
            except AssertionError:
                pass
            return -1


def collect_data(running_flag):
    """Collects data for face recognizer training.

    This function uses haar cascade face detection algorithm to snap
    30 grayscale photos of user's face, cropped to contain only facial
    region and saves them to disk. Photos formatted this way are ready
    to be used to train opencv's face recognition algorithms.

    Args:
        running_flag: flag for stopping this function early. Function
            is running while this flag is set.
            Type multiprocessing.Event is assumed.

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
        raise ValueError('resources/haarcascade_frontalface_alt2.xml not found')

    if not os.path.exists('../resources/training_data'):
        os.makedirs('../resources/training_data')

    pictures_taken_counter = 0

    while running_flag.is_set():

        ret, img = camera.read()
        grayscale_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        list_of_detected_faces = face_cascade_classifier.detectMultiScale(grayscale_img)

        if len(list_of_detected_faces) > 0:
            x, y, w, h = list_of_detected_faces[0]
            # Saves image cropped to only contain face region to disk.
            cv2.imwrite(TRAINING_DATA_PATH + 'face' + '_' + str(pictures_taken_counter) + '.jpg',
                        grayscale_img[y:y+h, x:x+w])
            pictures_taken_counter += 1
            cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)

        cv2.imshow('camera', img)

        if pictures_taken_counter == 30:
            running_flag.clear()
            break

        cv2.waitKey(500)

    camera.release()
    cv2.destroyAllWindows()
