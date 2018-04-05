import tkinter as tk
import json

from googleapiclient import discovery

from plugin import Plugin
import calendarapi


API_SERVICE_NAME = 'calendar'
API_VERSION = 'v3'
MAX_EVENT_COUNT = 10


class Calendar(tk.Frame, Plugin):
    """Displays google calendar events when face is recognized.

    This class inherits from tkinter's Frame class and abstract Plugin
    class. Google Calendar API is used to source events. Calendar will
    be displayed only when known face is recognized and that person
    logged in to Google Calendar at startup.
    """
    def __init__(self, master, controller):

        tk.Frame.__init__(self, master, bg='black', highlightbackground='black',
                          highlightthickness=2, cursor='none')

        self._controller = controller

        self._calendar_api = calendarapi.CalendarApiWrapper()

        self._face_recognizer = controller.get_face_recognizer()
        self._id_credentials_dict = controller.get_id_credentials_dict()
        self._framename_coords_dict = controller.get_framename_coords_dict()
        self._id_service_dict = dict()
        self._upcoming_events_list = list()
        self._events_colours = None
        self._upcoming_events_labels = list()
        self._build_calendar_discovery_dict()
        self._create_upcoming_events_labels()

        self._calendar_currently_displayed = False
        self._hiding_events_ongoing = False
        self._displaying_events_ongoing = False

        # Coordinates relative to this class' frame.
        self._mouse_left_button_click_x_cord = 0
        self._mouse_left_button_click_y_cord = 0

        self._events_count = 0
        self._events_iterator = 0

        # Variable for determining whether the edit mode should be
        # switched on or off.
        self._frame_in_edit_mode = False

        self._check_display_conditions()

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
            self._calendar_currently_displayed = True

            for i, event_label in enumerate(self._upcoming_events_labels):

                event_label.config(text='Edit mode', bg='#5484ED')
                event_label.grid(row=i, column=0, pady=5)
                event_label.bind('<Button-1>', self._mouse_left_button_click)
                event_label.bind('<B1-Motion>', self._mouse_left_button_motion)
                event_label.bind('<ButtonRelease-1>', self._mouse_left_button_release)

            self.config(highlightbackground='yellow', cursor='arrow')
            self.bind('<Button-1>', self._mouse_left_button_click)
            self.bind('<B1-Motion>', self._mouse_left_button_motion)
            self.bind('<ButtonRelease-1>', self._mouse_left_button_release)

        else:

            self._frame_in_edit_mode = False

            for event_label in self._upcoming_events_labels:
                event_label.unbind('<Button-1>')
                event_label.unbind('<B1-Motion>')
                event_label.unbind('<ButtonRelease-1>')
                event_label.grid_forget()

            self.config(highlightbackground='black', cursor='none')
            self.unbind('<Button-1>')
            self.unbind('<B1-Motion>')
            self.unbind('<ButtonRelease-1>')

            self._calendar_currently_displayed = False

    def _create_upcoming_events_labels(self):
        """Creates empty labels for upcoming events."""
        for i in range(MAX_EVENT_COUNT):
            self._upcoming_events_labels.append(tk.Label(self, font=('Helvetica', 25), width=20,
                                                         height=1, anchor='w',))

    def _build_calendar_discovery_dict(self):
        """Builds dict containing service objects for all stored credentials."""
        for key, value in self._id_credentials_dict.items():
            service = discovery.build(API_SERVICE_NAME, API_VERSION, credentials=value)
            self._id_service_dict[key] = service

    def _mouse_left_button_click(self, event):
        """Saves coordinates of left mouse button click relative to
        this class' frame."""
        if event.widget == self:
            # If user clicked on space between event labels event
            # coordinates are already relative to this class' frame.
            self._mouse_left_button_click_x_cord = event.x
            self._mouse_left_button_click_y_cord = event.y
        else:
            # If user clicked on event label mouse position is
            # calculated by adding mouse coordinates relative to label
            # to label's coordinates relative to this class' frame.
            self._mouse_left_button_click_x_cord = event.widget.winfo_x() + event.x
            self._mouse_left_button_click_y_cord = event.widget.winfo_y() + event.y

    def _mouse_left_button_motion(self, event):
        """Repositions frame according to mouse cursor movement while
        left button is pressed."""
        self.place(x=event.x_root - self._mouse_left_button_click_x_cord,
                   y=event.y_root - self._mouse_left_button_click_y_cord)
        coords = (event.x_root - self._mouse_left_button_click_x_cord,
                  event.y_root - self._mouse_left_button_click_y_cord)
        self._framename_coords_dict['Calendar'] = coords

    def _mouse_left_button_release(self, event):
        """Saves new position to json file."""
        with open('../resources/dicts/framename_coords_dict.json', 'w') as dict_json:
            json.dump(self._framename_coords_dict, dict_json)

    def _get_upcoming_events(self, person_id):
        """Invokes asynchronous api call and checks for results."""
        self._displaying_events_ongoing = True
        returncode, self._upcoming_events_list,\
            self._events_colours = self._calendar_api.get_upcoming_events()
        if returncode == -1:
            # Api call was not requested.
            self._calendar_api.call_calendar_api(self._id_service_dict[str(person_id)])
        if self._upcoming_events_list:
            self._events_count = len(self._upcoming_events_list)
            self._display_upcoming_events()
        else:
            # Calendar Api call results are not ready yet so we
            # schedule next check.
            self.after(200, self._get_upcoming_events, person_id)

    def _display_upcoming_events(self):
        """Displays calendar events one at a time."""
        # TODO Make event tabs scalable to the time lengths of events.
        if self._upcoming_events_list and not self._frame_in_edit_mode:
            event = self._upcoming_events_list[self._events_iterator]
            label = self._upcoming_events_labels[self._events_iterator]
            start_time = event['start']['dateTime'].split('T')[1]
            start_time = start_time.split(':')
            start_time = start_time[0] + ':' + start_time[1] + '  '
            # If event has default colour or no title set calendar api
            # does not provide this information so it has to be set to
            # default manually.
            try:
                color_id = event['colorId']
            except KeyError:
                color_id = '9'
            try:
                event_summary = event['summary']
            except KeyError:
                event_summary = 'No title'
            label.config(text=start_time+event_summary,
                         bg=self._events_colours['event'][color_id]['background'],
                         fg=self._events_colours['event'][color_id]['foreground'])
            label.grid(row=self._events_iterator, column=0, pady=5)
            self._events_iterator += 1
            if self._events_iterator < MAX_EVENT_COUNT\
               and self._events_iterator < self._events_count:
                self.after(50, self._display_upcoming_events)
            else:
                self._displaying_events_ongoing = False
                self._calendar_currently_displayed = True
                self._events_iterator = 0

    def _hide_upcoming_events_labels(self):
        """Removes all labels from grid geometry manager one at a time."""
        self._currently_hiding_events = True
        if not self._frame_in_edit_mode:
            self._upcoming_events_labels[self._events_iterator].grid_forget()
            self._events_iterator += 1
            if self._events_iterator < self._events_count:
                self.after(50, self._hide_upcoming_events_labels)
            else:
                self._currently_hiding_events = False
                self._calendar_currently_displayed = False
                self._events_iterator = 0

    def _check_display_conditions(self):
        """Checks for detected/recognized face and displays or hides
        calendar."""
        person_id = self._face_recognizer.get_recognized_face()
        if not self._calendar_currently_displayed:

            if person_id != -1:

                if person_id != 0 and str(person_id) in self._id_service_dict\
                   and not self._displaying_events_ongoing:
                    self._get_upcoming_events(person_id)
                    # We displayed calendar so next check is scheduled
                    # with bigger delay in case face accidentally
                    # doesn't get detected or recognized.
                    self.after(5000, self._check_display_conditions)
                else:
                    self.after(200, self._check_display_conditions)

            else:
                self.after(1000, self._check_display_conditions)

        elif not self._hiding_events_ongoing and not self._displaying_events_ongoing:

            if person_id == -1:
                self._hide_upcoming_events_labels()
                self.after(500, self._check_display_conditions)
            else:
                self.after(5000, self._check_display_conditions)

        else:
            self.after(500, self._check_display_conditions())
