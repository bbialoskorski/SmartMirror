import tkinter as tk
import json

from calendarauth import CalendarAuthenticator


class CalendarLoginPage(tk.Frame):
    """Menu page for logging into google calendar.

    CalendarLoginPage inherits from tkinter's frame page. It's purpose
    is to provide end user with interface to authenticate and authorize
    google calendar access.
    """
    def __init__(self, master, controller):
        tk.Frame.__init__(self, master)

        self._controller = controller
        # Every time this page is shown it will reset it's state to
        # default. This let's us update available user list in case
        # face recognizer was trained.
        self.bind('<<FrameShown>>', self._reset_page)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self._calendar_authenticator = CalendarAuthenticator()
        self._id_credentials_dict = controller.get_id_credentials_dict()
        self._id_name_dict = dict()
        self._name_id_dict = dict()

        self._user_listbox = tk.Listbox(self)
        self._user_login_button = tk.Button(self, text='Authenticate Calendar', relief=tk.GROOVE,
                                            command=self._authenticate_user)
        self._cancel_button = tk.Button(self, text='Cancel', relief=tk.GROOVE,
                                        state=tk.DISABLED, command=self._cancel_authentication)
        self._start_page_button = tk.Button(self, text='Go back', relief=tk.GROOVE,
                                            command=lambda: master.show_frame('StartPage'))

        self._user_listbox.grid(row=0, column=0, rowspan=4, pady=5)
        self._user_login_button.grid(row=2, column=1, padx=5, pady=5)
        self._cancel_button.grid(row=3, column=1, padx=5, pady=5)
        self._start_page_button.grid(row=5, column=0, columnspan=3, pady=5)

    def _reset_page(self, event):
        """Resets page's state and updates list of available users."""
        # Loading id_name_dict state from json file.
        with open('../resources/dicts/id_name_dict.json', 'r') as id_name_dict_json:
            self._id_name_dict = json.load(id_name_dict_json)

        # Removing all listbox entries and filling it with values from
        # newly loaded dictionary.
        self._user_listbox.delete(0, tk.END)

        for key, value in self._id_name_dict.items():
            self._name_id_dict[value] = key
            self._user_listbox.insert(tk.END, value)

    def _authenticate_user(self):
        """Starts calendar authentication for selected user."""
        index = self._user_listbox.curselection()
        if len(index) > 0:
            user_name = self._user_listbox.get(index[0])
            user_id = self._name_id_dict[user_name]
            self._user_login_button.config(state=tk.DISABLED)
            self._cancel_button.config(state=tk.ACTIVE)
            self._calendar_authenticator.start_authentication()
            self._save_credentials(user_id)

    def _save_credentials(self, user_id):
        """Saves user's credentials if authentication is completed."""
        # TODO Add pop up confirming that authentication has been
        # successfully completed.
        returncode, credentials = self._calendar_authenticator.get_credentials()

        if returncode == 0:
            self._id_credentials_dict[user_id] = credentials
            self._user_login_button.config(state=tk.ACTIVE)
            self._cancel_button.config(state=tk.DISABLED)
        else:
            # Authentication was not completed so we schedule this
            # function for later.
            self.after(200, self._save_credentials, user_id)

    def _cancel_authentication(self):
        """Stops authentication and resets buttons' state."""
        self._cancel_button.config(state=tk.DISABLED)
        self._user_login_button.config(state=tk.ACTIVE)
        self._calendar_authenticator.cancel_authentication()
