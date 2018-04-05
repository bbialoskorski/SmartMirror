import datetime as dt
import json

from plugin import Plugin
import tkinter as tk

TIME_FONT = ('Helvetica', 60)
DATE_FONT = ('Helvetica', 33)


class Clock(tk.Frame, Plugin):
    """Displays time and date.

    Clock class inherits from tkinter's Frame class and abstract
    Plugin class.
    """

    def __init__(self, master, controller):

        tk.Frame.__init__(self, master, bg='black', cursor='none', highlightbackground='black',
                          highlightthickness=2)

        self._controller = controller

        self._framename_coords_dict = controller.get_framename_coords_dict()

        self._frame_in_edit_mode = False
        self._mouse_left_button_click_x_cord = 0
        self._mouse_left_button_click_y_cord = 0

        # Creating labels of which this module consist.
        self._name_label_dict = dict()
        self._hours_label = tk.Label(self, bg='black', fg='white', font=TIME_FONT)
        self._minutes_label = tk.Label(self, bg='black', fg='white', font=TIME_FONT)
        self._colon_label = tk.Label(self, text=':', bg='black', fg='white', font=TIME_FONT)
        self._date_label = tk.Label(self, bg='black', fg='white', font=DATE_FONT, padx=0, pady=0)

        # Placing labels inside a grid geometry manager.
        self._hours_label.grid(row=0, column=0, sticky='nesw')
        self._minutes_label.grid(row=0, column=2, sticky='nesw')
        self._colon_label.grid(row=0, column=1, sticky='nesw')
        self._date_label.grid(row=1, columnspan=3)

        # Calling callback functions for the first time for updates
        # and clock tick animation.
        self._display_time()
        self._display_colon()
        self._display_date()

    def edit_mode(self):
        """Switches edit_mode on/off.

        When switching edit mode on this function first makes mouse
        cursor visible when on top of this module and makes background
        highlight visible by changing it's color to yellow, then
        appropriate event handlers are bind to left mouse button click
        (<Button-1>) and mouse motion with left mouse button pressed
        (<B1-Motion>) for every component.

        When switching edit mode off cursor is first hidden, highlight
        made invisible by changing it's color to black, then mouse
        input event handlers are unbound from all components.
        """

        if not self._frame_in_edit_mode:

            self._frame_in_edit_mode = True
            self.config(highlightbackground='yellow', cursor='arrow')
            for label in self.winfo_children():
                label.bind('<Button-1>', self._mouse_left_button_click)
                label.bind('<B1-Motion>', self._mouse_left_button_motion)
                label.bind('<ButtonRelease-1>', self._mouse_left_button_release)

        else:

            self._frame_in_edit_mode = False
            self.config(highlightbackground='black', cursor='none')
            for label in self.winfo_children():
                label.unbind('<B1-Motion>')
                label.unbind('<Button-1>')
                label.unbind('<ButtonRelease-1>')

    def _mouse_left_button_click(self, event):
        """Saves coordinates of left mouse button click relative to
        this class's frame."""
        # Saves the coordinates of left mouse button click relative to
        # this module's frame. These coordinates are calculated by
        # adding mouse event coordinates relative to Label on which
        # the user clicked to coordinates of said label relative to
        # this module's frame.
        self._mouse_left_button_click_x_cord = event.widget.winfo_x() + event.x
        self._mouse_left_button_click_y_cord = event.widget.winfo_y() + event.y

    def _mouse_left_button_motion(self, event):
        """Repositions frame according to mouse cursor movement while
        left button is pressed."""
        self.place(x=event.x_root - self._mouse_left_button_click_x_cord,
                   y=event.y_root - self._mouse_left_button_click_y_cord)
        self._framename_coords_dict['Clock'] = (event.x_root - self._mouse_left_button_click_x_cord,
                                                event.y_root - self._mouse_left_button_click_y_cord)

    def _mouse_left_button_release(self, event):
        """Saves new position to json file."""
        with open('../resources/dicts/framename_coords_dict.json', 'w') as dict_json:
            json.dump(self._framename_coords_dict, dict_json)

    def _display_time(self):
        """Updates labels with current time."""
        time = dt.datetime.time(dt.datetime.now())
        hour = str(time.hour)
        minute = time.strftime('%M')
        if len(hour) == 1:
            hour = '0' + hour
        self._hours_label.config(text=hour)
        self._minutes_label.config(text=minute)
        self.after(200, self._display_time)

    def _display_colon(self):
        """Displays blinking colon animation."""
        self.after(500, self._display_colon)
        next_color = 'black'
        # Colon is hidden by changing its foreground color to black.
        if self._colon_label.cget('foreground') == 'black':
            next_color = 'white'
        self._colon_label.config(fg=next_color)

    def _display_date(self):
        """Updates label with date everyday at midnight."""
        current_date = dt.datetime.now()
        time = dt.datetime.time(current_date)
        month = current_date.strftime('%b')
        weekday = current_date.strftime('%a')
        day = str(current_date.date().day)
        date = weekday + ', ' + month + ' ' + day
        self._date_label.config(text=date)
        # Setting date refresh time to 100 millisecond after midnight.
        callback_time = (23 - time.hour)*3600000 + (60 - time.minute)*60000 + 100
        self.after(callback_time, self._display_date)
