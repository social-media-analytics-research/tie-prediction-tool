"""
Log module to provide basic functionalities to set up logging with the standard python library.
"""

import logging
import os
from datetime import datetime


def set_up_logging(
    file_path: str = None,
    debug_level: str = 'ERROR',
    format_string_extension: str = None,
    log_to_console: bool = False,
    rotating_log_file: bool = False,
    log_header_config: dict = None
):
    """
    Set up logging settings.

    Args:
        file_path::str (=None)
            The path where the log file should be stored including the filename.
            Example: C:\\Users\\cs1111\\Documents\\MyProject\\my_log.log
            The date and time will be appended to the file
            Example: my_log.log -> my_log_%Y_%m_%d_%H%M%S.log
            If not specified then the log will be saved to the application's current location.
        debug_level::str (='ERROR')
            Logging debug level.
            Possible values: INFO, DEBUG, WARNING, ERROR
        format_string_extension::str (=None)
            String that extends the standard log output.
            Time and log level are always fix ('%(asctime)s %(levelname)s')
            but can be extended by name or message in a custom way.
            Default is: '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
            Refer to logging documentation for further information.
        log_to_console::bool (=False)
            Whether to include a StreamHandler that writes logs to the console as well.
            Log files will always be created whether log_to_console is set to True or False.
        rotating_log_file::bool (=False)
            Whether to append current date and time to the name of the log file.
        log_header_config::dict (=None)
            Header containing user-specified information about the application.
            A dict-entry with key \"Responsible\" and value \"John Doe\" would result in:
            \"Responsible: John Doe\"

    Info:
        Log entries can be assigned to different namespaces.
        Example:
        log = logging.getLogger('my_namespace')
        log.debug('my log message')
    """

    # Set file path
    logging_path = ''
    if file_path is None:
        dir_name = os.path.dirname(os.path.realpath(__file__))
        if rotating_log_file:
            file_name = _append_current_datetime(os.path.basename(dir_name))
        else:
            file_name = _append_extension(os.path.basename(dir_name))
        logging_path = os.path.join(
            dir_name,
            file_name
        )
    else:
        if rotating_log_file:
            logging_path = _append_current_datetime(file_path)
        else:
            logging_path = _append_extension(file_path)

    # Create header from dict
    if log_header_config is not None:
        try:
            with open(logging_path, 'w') as log_file:
                log_file.write('HEADER\n')
                for key, value in log_header_config.items():
                    log_file.write(str(key) + ': ' + str(value) + '\n')
                log_file.write('\nLOG ENTRIES\n')
        except Exception as general_exc:
            print('Exception while creating log file:\n', general_exc)

    #  Changing the root logger's level
    logger = logging.getLogger()
    logger.setLevel(_str_to_debug_level(debug_level))

    # The FileHandler is always active
    file_handler = logging.FileHandler(filename=logging_path, mode='a', delay=True)

    # Setting the format_string of the logs
    if format_string_extension is None:
        format_string_extension = '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
    else:
        format_string_extension = '%(asctime)s [%(levelname)s]' + \
            format_string_extension
    formatter = logging.Formatter(format_string_extension)
    file_handler.setFormatter(formatter)

    # Adding the file handler to the root logger
    logger.addHandler(file_handler)

    # Activate StreamHandler if wanted
    if log_to_console:
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)


def _str_to_debug_level(str_debug_level: str):
    """
    Transform string to log level and return it.
    """
    str_debug_level = str_debug_level.upper()
    if str_debug_level == 'INFO':
        return logging.INFO
    if str_debug_level == 'DEBUG':
        return logging.DEBUG
    if str_debug_level == 'WARNING':
        return logging.WARNING
    if str_debug_level == 'ERROR':
        return logging.ERROR
    return logging.ERROR


def _append_current_datetime(file_path: str):
    """
    Insert date and time into file path and return it.
    """
    now = datetime.now().strftime("%Y_%m_%d_%H%M%S")
    if file_path.endswith('.log'):
        return file_path.replace(file_path, f'_{now}.log')
    return f'{file_path}_{now}.log'


def _append_extension(file_path: str):
    """
    Insert .log into file path and return it.
    """
    if file_path.endswith('.log'):
        return file_path
    return f'{file_path}.log'
