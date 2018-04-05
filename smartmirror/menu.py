import tkinter as tk

from trainrecognizerpage import TrainRecognizerPage
from calendarloginpage import CalendarLoginPage


class Menu(tk.Frame):
    """Application menu.

    Menu class inherits from tkinter's Frame class. It acts as a
    controller and container for all options pages.
    """
    def __init__(self, master, controller):
        """Creates Menu frame and places all menu pages inside.

        Args:
            master: parent of this frame, usually direct container.
            controller: main window class providing public functions
                for control of the application from this frame's
                level.
        """
        tk.Frame.__init__(self, master, width=400, height=250)

        self._controller = controller

        # Dictionary for storing frames. Frame's key is it's class'
        # name.
        self._name_frame_dict = dict()
        self._name_frame_dict['StartPage'] = StartPage(self, controller)
        self._name_frame_dict['TrainRecognizerPage'] = TrainRecognizerPage(self, controller)
        self._name_frame_dict['CalendarLoginPage'] = CalendarLoginPage(self, controller)

        for key, value in self._name_frame_dict.items():
            # Places all frames in the same grid location so that only
            # top one is visible.
            value.grid(row=0, column=0, sticky='nesw')

        self.show_frame('StartPage')

    def show_frame(self, frame_key):
        """Brings frame to the top and sends it <<FrameShown>> event.

        Args:
            frame_key: dictionary key of frame that we want to show.
                       Frame's key is it's class' name.
        """
        self._name_frame_dict[frame_key].tkraise()
        self._name_frame_dict[frame_key].event_generate('<<FrameShown>>')


class StartPage(tk.Frame):
    """Menu's 'base' page.

    StartPage inherit's from tkinter's frame class. It acts as a
    container of buttons used to navigate to different menu pages.
    """
    def __init__(self, master, controller):

        tk.Frame.__init__(self, master)

        self._controller = controller
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self._train_recognizer_button = tk.Button(self, text='Add Face', relief=tk.GROOVE,
                                                  command=lambda:
                                                  master.show_frame('TrainRecognizerPage'))
        self._calendar_login_button = tk.Button(self, text='Log in to Calendar', relief=tk.GROOVE,
                                                command=lambda:
                                                master.show_frame('CalendarLoginPage'))
        self._start_smartmirror_button = tk.Button(self, text='Start SmartMirror',
                                                   relief=tk.GROOVE,
                                                   command=lambda: controller.start_smartmirror())
        self._train_recognizer_button.grid(row=0, column=0, pady=5)
        self._calendar_login_button.grid(row=1, column=0, pady=5)
        self._start_smartmirror_button.grid(row=2, column=0, pady=5)
