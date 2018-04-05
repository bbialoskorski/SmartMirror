import os
import json
import random
import tkinter as tk

from recognizertraining import train_recognizer
import trainingdata

TRAINING_DATA_PATH = '../resources/training_data/'


class TrainRecognizerPage(tk.Frame):
    """Menu page with face recognition training interface.

    TrainRecognizerPage inherits from tkinter's frame page. It stores
    all widgets inside a grid geometry manager and implements
    functions bind to these widgets. It's purpose is to provide end
    user with interface to collect training data and train face
    recognition module with his/hers face.
    """
    def __init__(self, master, controller):
        tk.Frame.__init__(self, master)

        self._controller = controller
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self._data_collector = trainingdata.TrainingData()
        self._collecting_training_data = False
        self._id_name_dict = dict()
        self._load_id_name_dict()

        self._reset_button = tk.Button(self, text='Reset', relief=tk.GROOVE, state=tk.DISABLED,
                                       command=self._reset_page)
        self._start_page_button = tk.Button(self, text='Go back', relief=tk.GROOVE,
                                            command=self._go_to_start_page)
        self._collect_training_data_button = tk.Button(self, text='Collect training data',
                                                       relief=tk.GROOVE,
                                                       command=self._collect_training_data)
        self._train_button = tk.Button(self, text='Train', relief=tk.GROOVE, state=tk.DISABLED,
                                       command=self._train_recognizer)
        self._info_label = tk.Label(self, text='Enter your name:')
        self._name_entry_box = tk.Entry(self)
        # TODO Add format control to the entry widget.
        self._info_label.grid(row=0, column=0, columnspan=3, pady=5)
        self._name_entry_box.grid(row=1, column=0, columnspan=2, pady=5)
        self._collect_training_data_button.grid(row=2, column=0, padx=5)
        self._train_button.grid(row=2, column=1, padx=5)
        self._reset_button.grid(row=3, column=0, columnspan=2, pady=5)
        self._start_page_button.grid(row=4, column=0, columnspan=2, pady=5)

    def _go_to_start_page(self):
        """Raises menu start page to the top and resets it's state."""
        self._reset_page()
        self.master.show_frame('StartPage')

    def _reset_page(self):
        """Resets this page's state and clears training data folder."""
        for file in os.listdir(TRAINING_DATA_PATH):
            file_path = os.path.join(TRAINING_DATA_PATH, file)
            if os.path.isfile(file_path):
                os.unlink(file_path)
        self._collecting_training_data = False
        self._data_collector.stop_collector()
        self._collect_training_data_button.config(state=tk.ACTIVE)
        self._train_button.config(state=tk.DISABLED)

    def _load_id_name_dict(self):
        """Loads dictionary mapping id to name from json file."""
        with open('../resources/dicts/id_name_dict.json', 'r') as id_name_dict_json:
            self._id_name_dict = json.load(id_name_dict_json)

    def _collect_training_data(self):
        """Collects pictures of user's face."""
        self._collect_training_data_button.config(state=tk.DISABLED)
        self._reset_button.config(state=tk.ACTIVE)
        self._collecting_training_data = True
        self._data_collector.collect_data()
        self._is_data_collected()

    def _is_data_collected(self):
        """Checks if training data has been collected.

        If data was collected 'train' button becomes enabled, else
        another check is scheduled.
        """
        if self._collecting_training_data:
            if not self._data_collector.is_running():
                self._train_button.config(state=tk.ACTIVE)
                self._reset_button.config(state=tk.DISABLED)
                self._collecting_training_data = False
            else:
                self.after(200, self._is_data_collected)

    def _train_recognizer(self):
        """Trains recognizer.

        Trains recognizer, then maps user's name to newly assigned id
        and saves modified dictionary to a json file.
        """
        name = self._name_entry_box.get()
        self._name_entry_box.delete(0, tk.END)
        new_id = random.randint(1000, 9999)
        while str(new_id) in self._id_name_dict:
            new_id = random.randint(1000, 9999)

        train_recognizer(new_id)
        # Storing updated dict inside a json file.
        self._id_name_dict[new_id] = name
        with open('../resources/dicts/id_name_dict.json', 'w') as id_name_dict_json:
            json.dump(self._id_name_dict, id_name_dict_json)
        self._train_button.config(state=tk.DISABLED)
        self._collect_training_data_button.config(state=tk.ACTIVE)
