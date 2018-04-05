import tkinter as tk
import json

from plugin import Plugin

GREET_FONT = ('Helvetica', 80)


class Greeter(tk.Frame, Plugin):
    """Greeter module class.

    Greeter class inherits from tkinter's Frame class and abstract
    Plugin class. This modules displays greetings message when face is
    detected and recognized.
    """

    def __init__(self, master, controller):

        tk.Frame.__init__(self, master, bg='black', highlightbackground='yellow', cursor='none')

        self._controller = controller
        self._message_label = tk.Label(self, fg='white', bg='black', font=GREET_FONT)
        self._face_recognizer = controller.get_face_recognizer()
        self._id_name_dict = dict()
        self._framename_coords_dict = controller.get_framename_coords_dict()
        self._load_id_name_dict()
        # Set of people for which notification was recently displayed.
        self._recent_visitors = set()
        # Coordinates relative to this class' frame.
        self._mouse_left_button_click_x_cord = 0
        self._mouse_left_button_click_y_cord = 0
        # Variable for determining whether the edit mode should be
        # switched on or off.
        self._frame_in_edit_mode = False
        self._check_display_conditions()

    def edit_mode(self):
        """Switches edit_mode on/off.

        When switching edit mode on this function first makes mouse
        cursor visible while hovering on top of this module and makes
        background highlight visible by changing it's color to yellow,
        then appropriate event handlers are bind to left mouse button
        click (<Button-1>) and mouse motion with left mouse button
        pressed (<B1-Motion>) for every component.

        When switching edit mode off cursor is first hidden, highlight
        made invisible by changing it's color to black, then mouse
        input event handlers are unbound from all components.
        """

        if not self._frame_in_edit_mode:

            self._frame_in_edit_mode = True
            self.config(highlightthickness=2, cursor='arrow')
            self._message_label.config(text='Hi Sexy!')
            self._message_label.grid(row=0, column=0)
            for label in self.winfo_children():
                label.bind('<Button-1>', self._mouse_left_button_click)
                label.bind('<B1-Motion>', self._mouse_left_button_motion)
                label.bind('<ButtonRelease-1>', self._mouse_left_button_release)

        else:

            self._frame_in_edit_mode = False
            self.config(highlightthickness=0, cursor='none')
            self._message_label.grid_forget()
            for label in self.winfo_children():
                label.unbind('<Button-1>')
                label.unbind('<B1-Motion>')
                label.unbind('<ButtonRelease-1>')

    def _load_id_name_dict(self):
        """Loads dictionary mapping id to name from json file."""
        with open('../resources/dicts/id_name_dict.json', 'r') as id_name_dict_json:
            self._id_name_dict = json.load(id_name_dict_json)

    def _mouse_left_button_click(self, event):
        """Saves coordinates of left mouse button click relative to
        this class' frame."""
        # These coordinates are calculated by adding mouse event coordinates
        # relative to Label on which the user clicked to coordinates of said
        # label relative to this class's frame.
        self._mouse_left_button_click_x_cord = event.widget.winfo_x() + event.x
        self._mouse_left_button_click_y_cord = event.widget.winfo_y() + event.y

    def _mouse_left_button_motion(self, event):
        """Repositions frame according to mouse cursor position."""
        self.place(x=event.x_root - self._mouse_left_button_click_x_cord,
                   y=event.y_root - self._mouse_left_button_click_y_cord)
        coords = (event.x_root - self._mouse_left_button_click_x_cord,
                  event.y_root - self._mouse_left_button_click_y_cord)
        self._framename_coords_dict['Greeter'] = coords

    def _mouse_left_button_release(self, event):
        """Saves new position to json file."""
        with open('../resources/dicts/framename_coords_dict.json', 'w') as dict_json:
            json.dump(self._framename_coords_dict, dict_json)

    def _check_display_conditions(self):
        """Checks if known face was recognized.
        For recognized face calls _greet function to display message."""
        if not self._frame_in_edit_mode:

            person_id = self._face_recognizer.get_recognized_face()

            if person_id != -1:
                if person_id != 0 and person_id not in self._recent_visitors:

                    try:
                        name = self._id_name_dict[str(person_id)]
                    except KeyError:
                        raise ValueError('This person`s name is missing from dict.')
                    self._display_message(name)
                    # Adding id of recognized face to dictionary to
                    # prevent displaying multiple messages for the
                    # same person in short time span. Scheduling
                    # removal of this id after some time.
                    self._recent_visitors.add(person_id)
                    self.after(900000, lambda user_id: self._recent_visitors.remove(user_id),
                               person_id)

        self.after(1000, self._check_display_conditions)

    def _display_message(self, name):
        """Displays greetings message for a provided name."""
        greet_message = 'Hi ' + name + '!'
        self._message_label.grid(row=0, column=0)
        self._message_label.config(text=greet_message)
        self.after(5000, func=self._message_label.grid_forget)
