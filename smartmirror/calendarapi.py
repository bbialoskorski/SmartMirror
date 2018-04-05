import datetime
import multiprocessing
import queue


class CalendarApiWrapper:
    """Google Calendar API wrapper for performing asynchronous calls."""
    def __init__(self):

        self._input_queue = multiprocessing.Queue(maxsize=1)
        self._output_queue = multiprocessing.Queue(maxsize=1)
        self._api_call_process = multiprocessing.Process(target=calendar_api_call,
                                                         daemon=True,
                                                         args=(self._input_queue,
                                                               self._output_queue,))

    def call_calendar_api(self, service):
        """Starts asynchronous api call.

        Only one request can be processed at the same time for each
        instance of CalendarApiWrapper.
        To obtain results get_upcoming_events() has to be called.

        Args:
            service: googleapiclient discovery's service object built
                for calendar v3 api with which the call will be made.
        Returns:
            0 if api was successfully called or 1 if api call is
            already processing

        Raises:
            ValueError: if impossible behaviour occurred.
        """
        if not self._api_call_process.is_alive():
            try:
                # Api process is not running so we put arguments
                # into the input queue.
                self._input_queue.put(service, block=False)
            except queue.Full:
                raise ValueError('Input queue was full. This should never happen.')

            try:
                self._api_call_process.start()
            except AssertionError:
                # This exception means that our process was already
                # started and finished execution so we join it and
                # then create and start a new one.
                self._api_call_process.join()
                self._api_call_process = multiprocessing.Process(target=calendar_api_call,
                                                                 daemon=True,
                                                                 args=(self._input_queue,
                                                                       self._output_queue,))
                self._api_call_process.start()
            return 0

        return 1

    def get_upcoming_events(self):
        """Checks availability and returns api call results.

        Returns:
            -1 if api's function was not called, 0 if api call
            finished and returned results or 1 if api call is being
            processed.

            upcoming_events: list of upcoming events.

            events_colours: dictionary containing calendar's colours
            data.
        """
        upcoming_events = None
        events_colours = None
        if self._api_call_process.is_alive():
            returncode = 1
        else:
            try:
                upcoming_events, events_colours = self._output_queue.get(block=False)
                self._api_call_process.join()
                returncode = 0
            except queue.Empty:
                returncode = -1
        return returncode, upcoming_events, events_colours


def calendar_api_call(input_queue, output_queue):
    """Callback function calling calendar api for upcoming events.

    Input should be added to the queue before this callback starts
    execution.

    Args:
        input_queue: queue for passing input. This function expects to
            get googleapiclient discovery's service object from this
            queue.
        output_queue: queue for passing call's results. Results are
            returned as a single 2 element tuple. First element is a
            list of upcoming calendar events, the second one is a dict
            containing calendar's color definitions.

    Raises:
        ValueError: if no arguments were passed through input queue.
    """
    try:
        service = input_queue.get(block=True, timeout=1)
    except queue.Empty:
        raise ValueError('Input queue empty.')
    lower_time_bound = datetime.datetime.utcnow().isoformat() + 'Z'
    upper_time_bound = datetime.datetime.utcnow()
    upper_time_bound = upper_time_bound.replace(hour=23, minute=59, second=59)
    upper_time_bound = upper_time_bound.isoformat() + 'Z'
    calendar_list = service.events().list(calendarId='primary', timeMin=lower_time_bound,
                                          timeMax=upper_time_bound, maxResults=10,
                                          singleEvents=True, orderBy='startTime').execute()
    upcoming_events = calendar_list.get('items', [])
    events_colours = service.colors().get().execute()
    try:
        output_queue.put((upcoming_events, events_colours), block=False)
    except queue.Full:
        # This exception will occur if previous request's results were
        # not collected with get_upcoming_events(). Replacing old
        # results with new.
        output_queue.get(block=True, timeout=1)
        output_queue.put((upcoming_events, events_colours), block=False)
