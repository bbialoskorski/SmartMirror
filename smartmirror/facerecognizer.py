import multiprocessing
import ctypes

from facerecognition import face_recognition


class FaceRecognizer:
    """Manages asynchronous face detection and recognition.

    This class hides multiprocessing mechanism details from the
    outside world.
    """
    def __init__(self):

        self._running_flag = multiprocessing.Event()
        self._recognized_face = multiprocessing.Value(ctypes.c_int, -1)
        self._recognizer_process = multiprocessing.Process(target=face_recognition,
                                                           daemon=True,
                                                           args=(self._running_flag,
                                                                 self._recognized_face,))
        self._running_flag.set()
        self._recognizer_process.start()

    def is_running(self):
        """Checks whether recognizer process is running.

        Returns:
            bool value.
        """
        return self._recognizer_process.is_alive()

    def get_recognized_face(self):
        """Return detection/recognition results.

        Returns:
            0 if face was detected but not recognized, 1 if no face
            was detected or id if face was detected and recognized.
        """
        return self._recognized_face.value

    def stop_face_recognition(self):
        """Finishes face detection and recognition process.

        This function MUST BE called before exiting application or
        recognition process will become orphan.

        Returns:
            0 if process was running and successfully stopped or 1 if
            process was not running.
        """
        # TODO Find more desirable way of guaranteeing that the
        # process will finish, optimally isolating outside user
        # from knowledge of any process being run.
        if self._recognizer_process.is_alive():
            self._running_flag.clear()
            self._recognizer_process.join()
            return 0
        return -1
