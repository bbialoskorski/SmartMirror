from abc import ABC, abstractmethod


class Plugin(ABC):
    """Abstract class which frames stored in MirrorDisplay class
     should inherit from."""
    @abstractmethod
    def edit_mode(self):
        """Puts frame in edit state.

        Implementation of this function should enable user to change
        location of frame using mouse input, concretely mouse motion
        with left mouse button pressed (<B1-Motion>).
        Yellow background highlight should be displayed around frame
        which is in edit state.
        """
        pass
