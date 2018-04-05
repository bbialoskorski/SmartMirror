import multiprocessing
import queue

from google_auth_oauthlib.flow import InstalledAppFlow

CLIENT_SECRET_FILE = '../resources/client_secret.json'
SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
REDIRECT_URI = 'http://localhost'


class CalendarAuthenticator:
    """Wrapper for asynchronous authentication with OAuth 2.0.

    CalendarAuthenticator uses multiprocessing module to handle
    asynchronous google calendar api authentication with readonly
    permissions. Authentication is started by calling
    start_authentication() and resulting credentials can be collected
    via get_credentials().
    Only one authentication can be performed at the same time for
    each instance of CalendarAuthenticator.
    During authentication process web browser is opened on google
    log in page through which user has to authenticate and confirm
    that he's giving this application permissions to access calendar
    information.
    """
    def __init__(self):

        self._output_queue = multiprocessing.Queue(maxsize=1)
        self._authenticator_process = multiprocessing.Process(target=get_credentials,
                                                              daemon=True,
                                                              args=(self._output_queue,))

    def start_authentication(self):
        """Starts authentication process.

        Only one authentication can be performed at the same time for
        each instance of CalendarAuthenticator.
        To obtain credentials get_credentials() has to be called.

        Returns:
            0 if authentication process was successfully started or 1
            if authentication process was already running.
        """
        if not self._authenticator_process.is_alive():
            try:
                self._authenticator_process.start()
            except AssertionError:
                # This exception means that our process was already
                # started and finished execution so we join it and
                # then create and start a new one.
                self._authenticator_process.join()
                self._authenticator_process = multiprocessing.Process(target=get_credentials,
                                                                      daemon=True,
                                                                      args=(self._output_queue,))
                self._authenticator_process.start()
            return 0

        return 1

    def get_credentials(self):
        """Return credentials and according return code.

        This function checks whether user completed authentication and
        returns credentials.

        Returns:
            -1 if authentication process was not started, 0 if
            authentication was completed or 1 if authentication is
            still ongoing.

            credentials: OAuth 2.0 credentials required to call
            calendar api.
        """
        credentials = None

        if self._authenticator_process.is_alive():
            returncode = 1
        else:
            try:
                credentials = self._output_queue.get(block=False)
                self._authenticator_process.join()
                returncode = 0
            except queue.Empty:
                returncode = -1

        return returncode, credentials

    def cancel_authentication(self):
        """Stops the authentication process.

        This function stops data collector process.
        Even if process was not running this function will attempt to
        join it.

        Returns:
            -1 if authentication process wasn't running or 0 if
            authentication was ongoing and successfully stopped.
        """
        if self._authenticator_process.is_alive():
            self._authenticator_process.terminate()
            self._authenticator_process.join()
            return 0
        else:
            try:
                self._authenticator_process.join()
            except AssertionError:
                pass
            return -1


def get_credentials(output_queue):
    """Executes authentication flow.

    This function executes OAuth 2.0 authentication flow for installed
    applications. Local server is started and web browser opens with
    google authentication page.

    Args:
        output_queue: queue through which credentials will be returned.
    """
    # TODO handle exception raised when user declines permission
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, scopes=[SCOPES])

    credentials = flow.run_local_server()

    try:
        output_queue.put(credentials, block=False)
    except queue.Full:
        # This exception will occur if credentials from previous
        # authentication were not collected with get_credentials().
        # Replacing old credentials with new.
        output_queue.get(block=True, timeout=1)
        output_queue.put(credentials, block=False)
