import tkinter as tk

import clock
import weather
import greeter
import smartcalendar


class MirrorDisplay(tk.Frame):
    """Creates and manages all information displaying modules.

    MirrorDisplay class inherits from tkinter's Frame class. It is
    a geometry master and controller for all frames stored inside.
    Each frame stored here has a role of displaying information to
    user.
    Once this frame is displayed application can be closed with Escape
    button.

    Every frame stored directly in MirrorDisplay should inherit from
    plugin abstract class thus implementing one specific public
    function: 'edit_mode'.
    This function should enable user to change location of module
    using mouse input, concretely mouse motion with left mouse button
    pressed (<B1-Motion>). Yellow background highlight should be
    displayed around each frame in edit state.
    """
    def __init__(self, master, controller):
        """Creates MirrorDisplay frame and places all plugin frames inside.

        Args:
            master: parent of this frame, usually direct container.
            controller: main window class providing public functions
                for control of the application from this frame's
                level.
        """
        tk.Frame.__init__(self, master, width=1080, height=2560, cursor='none', bg='black')

        self._controller = controller

        # Binding keyboard event to application's main window.
        controller.bind('<Tab>', self._edit_mode)

        self._framename_coords_dict = controller.get_framename_coords_dict()
        self._window_in_edit_mode = False

        # Initializing frames passing self as a master and controller
        # into the init functions.
        self._clock = clock.Clock(self, controller)
        self._weather = weather.Weather(self, controller)
        self._greeter = greeter.Greeter(self, controller)
        self._smartcalendar = smartcalendar.Calendar(self, controller)

        # Placing frames on the main frame using place geometry
        # manager (module's frames should be placed only with place
        # manager).
        self._place_frames()

        # Setting keyboard focus so we can use keyboard bindings
        # without clicking on the window first.
        self.focus_set()

    def _place_frames(self):
        """Places coordinates in place geometry manager."""
        self._clock.place(x=self._framename_coords_dict['Clock'][0],
                          y=self._framename_coords_dict['Clock'][1])
        self._weather.place(x=self._framename_coords_dict['Weather'][0],
                            y=self._framename_coords_dict['Weather'][1])
        self._greeter.place(x=self._framename_coords_dict['Greeter'][0],
                            y=self._framename_coords_dict['Greeter'][1])
        self._smartcalendar.place(x=self._framename_coords_dict['Calendar'][0],
                                  y=self._framename_coords_dict['Calendar'][1])

    def _edit_mode(self, event):
        """Switches edit_mode on/off.

        When switching edit mode on/off this function makes mouse
        cursor visible/invisible on the main frame. In either case
        edit_mode function is invoked for every displayable element
        stored inside a surface frame. Each module should individually
        handle the state in which it's currently in and appropriate
        state transition once edit_mode function is called again.
        """
        if not self._window_in_edit_mode:
            self._window_in_edit_mode = True
            self.config(cursor='arrow')
        else:
            self._window_in_edit_mode = False
            self.config(cursor='none')
        for frame in self.winfo_children():
            frame.edit_mode()
