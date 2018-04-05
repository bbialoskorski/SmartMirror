import json
import tkinter as tk

from menu import Menu
from mirrordisplay import MirrorDisplay
from facerecognizer import FaceRecognizer


class SmartMirror(tk.Tk):
    """Main window of the application.

    SmartMirror inherits from tkinter's Tk class. It manages 'main'
    frames and provides public functions needed to control the
    application from within these frames.
    Once start_smartmirror() is called application has to be closed
    using Escape key.
    """
    def __init__(self):

        tk.Tk.__init__(self)

        self.title("SmartMirror")

        # Dictionary for storing users' Calendar API credentials.
        self._id_credentials_dict = dict()
        self._framename_coords_dict = dict()
        self._face_recognizer = None
        self._load_coordinates_dict()

        self._menu_frame = Menu(self, self)
        self._mirror_display_frame = None

        self._menu_frame.grid(row=0, column=0)

    def start_smartmirror(self):
        """Creates and displays mirror display frame."""
        self._face_recognizer = FaceRecognizer()
        self._mirror_display_frame = MirrorDisplay(self, self)
        self.bind('<Escape>', self._stop_smartmirror)
        # Sets this window to fullscreen and makes it stay on top of
        # every other window.
        self.wm_attributes('-fullscreen', True, '-topmost', True)
        self._mirror_display_frame.grid(row=0, column=0)

    def _stop_smartmirror(self, event):
        """Performs necessary clean up and destroys root window."""
        if self._face_recognizer:
            self._face_recognizer.stop_face_recognition()
        self.destroy()

    def get_face_recognizer(self):
        """Return FaceRecognizer object."""
        return self._face_recognizer

    def get_id_credentials_dict(self):
        """Return dictionary mapping user id to calendar credentials."""
        return self._id_credentials_dict

    def get_framename_coords_dict(self):
        """Returns dictionary mapping frames' names to coordinates."""
        return self._framename_coords_dict

    def _load_coordinates_dict(self):
        """Loads dict mapping frame names to coordinates from json."""
        with open('../resources/dicts/framename_coords_dict.json', 'r') as dict_json:
            self._framename_coords_dict = json.load(dict_json)
