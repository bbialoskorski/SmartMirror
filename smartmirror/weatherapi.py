import requests
import multiprocessing
import queue

IP_INFO = 'http://ipinfo.io/json'
API_KEY = 'c67a801854866dfb'
API_ADDRESS = 'http://api.wunderground.com/api/'
API_CONDITIONS = '/conditions/q/'
TEMPERATURE_SCALE = 'c'


class WeatherApiWrapper:
    """Wunderground api wrapper for performing asynchronous requests.

    WeatherApiWrapper uses multiprocessing module to handle
    asynchronous wunderground api requests. Request can be started by
    calling call_weather_api() and response converted to json file can
    be collected with get_weather().
    Only one request can be processed at the same time for each
    instance of WeatherApiWrapper.
    """
    def __init__(self):

        self._input_queue = multiprocessing.Queue(maxsize=1)
        self._output_queue = multiprocessing.Queue(maxsize=1)
        self._api_call_process = multiprocessing.Process(target=weather_api_request,
                                                         daemon=True,
                                                         args=(self._input_queue,
                                                               self._output_queue,))

    def call_weather_api(self, country, region):
        """Starts asynchronous api request.

        Only one request can be processed at the same time for each
        instance of WeatherApiWrapper.
        To obtain results get_weather() has to be called.

        Args:
            country: country of interest. Either abbreviation or full
                english name.
            region: region of interest e.g city/province.
        Returns:
            0 if weather api request was successfully made or 1 if api
            request is already processing.

        Raises:
            ValueError: If impossible behaviour occurred.
        """
        if not self._api_call_process.is_alive():
            try:
                # Request process is not running so we put arguments
                # into the input queue.
                self._input_queue.put((country, region), block=False)
            except queue.Full:
                raise ValueError("Input queue was full. This should never happen.")

            try:
                self._api_call_process.start()
            except AssertionError:
                # This exception means that our process was already
                # started and finished execution so we join it and
                # then create and start a new one.
                self._api_call_process.join()
                self._api_call_process = multiprocessing.Process(target=weather_api_request,
                                                                 daemon=True,
                                                                 args=(self._input_queue,
                                                                       self._output_queue,))
                self._api_call_process.start()
            return 0

        return 1

    def get_weather(self):
        """Return request results and according return code.

        Returns:
            returncode:
                -1 if no request was made with call_weather_api
                function, 0 if weather information was successfully
                returned or 1 if api request is still being processed.
            weather_json: json file containing weather information for
                requested region or None (see returncode = -1 or 1).
        """
        weather_json = None
        if self._api_call_process.is_alive():
            returncode = 1
        else:
            try:
                weather_json = self._output_queue.get(block=False)
                self._api_call_process.join()
                returncode = 0
            except queue.Empty:
                returncode = -1

        return returncode, weather_json


def weather_api_request(input_queue, output_queue):
    """Callback function performing weather information requests.

    Args:
        input_queue: queue for passing city and region arguments for
            api request. These arguments should be passed in one
            tuple.
        output_queue: queue for passing request results.

    Raises:
        ValueError: if no arguments were passed through the input
            queue.
    """
    try:
        location = input_queue.get(block=True, timeout=1)
        country = location[0]
        region = location[1]
    except queue.Empty:
        raise ValueError('Input queue empty.')
    response = requests.get(API_ADDRESS + API_KEY + API_CONDITIONS + country + '/' + region
                            + '.json')
    weather_json = response.json()
    try:
        output_queue.put(weather_json, block=False)
    except queue.Full:
        # This exception will occur if previous request's results were
        # not collected with get_weather(). Replacing old results with
        # new.
        output_queue.get(block=True, timeout=1)
        output_queue.put(weather_json, block=False)
