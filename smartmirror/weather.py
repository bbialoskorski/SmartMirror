import requests
import json
import os

import tkinter as tk

from plugin import Plugin
import weatherapi
from weathericons import load_weather_icons

IP_INFO = 'http://ipinfo.io/json'
API_KEY = 'c67a801854866dfb'
API_ADDRESS = 'http://api.wunderground.com/api/'
API_CONDITIONS = '/conditions/q/'
TEMPERATURE_SCALE = 'c'
TEMPERATURE_FONT = ('Calibri Light', 55)


class Weather(tk.Frame, Plugin):
    """Weather module class.

    Weather class inherits from tkinter's Frame class and abstract
    Plugin class. This module displays weather conditions as an icon
    and current temperature in Fahrenheit or Celsius scale depending
    on user's preference.

    Ipinfo api is used for finding current location and weather
    underground api is used for polling weather information.
    """

    def __init__(self, master, controller):

        tk.Frame.__init__(self, master, bg='black', highlightbackground='black',
                          highlightthickness=2, cursor='none')

        self._controller = controller

        self._weather_api = weatherapi.WeatherApiWrapper()

        # Creating a dictionary of weather icons.
        self._weather_icons = load_weather_icons()
        self._framename_coords_dict = controller.get_framename_coords_dict()
        self._location = list()

        # Finding user's current location.
        self._get_location()

        self._weather_label = tk.Label(self, bg='black')
        self._temperature_label = tk.Label(self, bg='black')

        # Placing labels inside a grid geometry manager.
        self._weather_label.grid(row=0, column=0, sticky='nesw')
        self._temperature_label.grid(row=0, column=1, sticky='ns')

        # Coordinates relative to this class' frame.
        self._mouse_left_button_click_x_cord = 0
        self._mouse_left_button_click_y_cord = 0

        # Variable for determining whether the edit mode should be
        # switched on or off.
        self._frame_in_edit_mode = False

        self._display_current_weather_and_temperature()

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
                label.unbind('<Button-1>')
                label.unbind('<B1-Motion>')
                label.unbind('<ButtonRelease-1>')

    def _mouse_left_button_click(self, event):
        """Saves coordinates of left mouse button click relative to
        this class's frame."""
        # Saves coordinates of left mouse button click relative to
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
        coords = (event.x_root - self._mouse_left_button_click_x_cord,
                  event.y_root - self._mouse_left_button_click_y_cord)
        self._framename_coords_dict['Weather'] = coords

    def _mouse_left_button_release(self, event):
        """Saves new position to json file."""
        with open('../resources/dicts/framename_coords_dict.json', 'w') as dict_json:
            json.dump(self._framename_coords_dict, dict_json)

    def _get_location(self):
        """Determines current location using ip."""
        response = requests.get(IP_INFO)
        location_json = response.json()
        self._location.append(location_json['country'])
        self._location.append(location_json['city'])

    def _display_current_weather_and_temperature(self):
        """Updates labels with current weather and temperature."""
        # Weather underground api call.
        returncode, weather_json = self._weather_api.get_weather()
        if returncode == -1:
            self._weather_api.call_weather_api(self._location[0], self._location[1])
        if weather_json:
            # Extracting icon name from icon_url provided in returned
            # json by removing path to the file, and then removing
            # file extension. This is the only way to distinct daytime
            # and nighttime on the api level.
            icon_url = weather_json['current_observation']['icon_url']
            icon = os.path.basename(icon_url)
            icon = os.path.splitext(icon)[0]
            temp_scale = 'temp_' + TEMPERATURE_SCALE
            temperature_text = ' ' + str(weather_json['current_observation'][temp_scale])\
                               + '\N{DEGREE SIGN}'
            self._weather_label.config(image=self._weather_icons[icon])
            self._temperature_label.config(text=temperature_text, font=TEMPERATURE_FONT,
                                           fg='white')
            self.after(900000, self._display_current_weather_and_temperature)
        else:
            self.after(500, self._display_current_weather_and_temperature)