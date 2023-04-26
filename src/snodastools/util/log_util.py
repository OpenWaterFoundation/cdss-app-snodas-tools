"""
Utility functions for logging.
"""

import datetime
import getpass
import logging
import os
from pathlib import Path
import platform


def initialize_logging(app_name: str = None, logfile_name: Path = None, logfile_log_level: int = logging.INFO,
                       console_log_level: int = logging.WARNING):
    """
    Initialize logging for an application, using the Python logging module.
    This function can be called by applications to set up the initial logfile.
    Named parameters should be used to ensure proper handling of parameters.
    The following is configured:

    Logger:
        - logger name is "snodastools" so that all modules can inherit
          (consequently, using the logger from a main application should request logger "snodastools"
          since the __name__ will be '__main__').
        - log formatter = '%(levelname)s|%(module)s line %(lineno)d|%(message)s'
          By default the format does not include the date/time because this eats up log file space.
          If necessary, print the time to indicate start/end of processing.
        - FileHandler is initialized corresponding to logfile_name with level INFO.

    Args:
        app_name (str):           Name of the application, written to top of log file.
        logfile_name (str):       Name of the initial log file, None indicates no logfile.
        logfile_log_level (int):  The logging level for the log file (default is logging.INFO).
        console_log_level (int):  Console log level (default is logging.ERROR),
                                  use logging.NOTSET for no console logging.

    Returns:
        The logger that is created.
    """

    global __logfile_handler, __logfile_name
    log_formatter = logging.Formatter('%(levelname)s|%(name)s|%(module)s line %(lineno)d|%(message)s')
    console_formatter = logging.Formatter('%(levelname)s: %(message)s')

    # Request a logger for the 'snodastools', which will create a new logger since not previously found:
    # - use "snodastools" for the name, which matches the top-level package name
    # - all requests in library code using __name__ will therefore match the root module name
    # - this also allows the __main__ program to request a logger with name "snodastools" so that
    #   messages can be written to the same log file
    logger_name = "snodastools"
    logger = logging.getLogger(logger_name)

    # Set the logger level to DEBUG because it needs to handle all levels:
    # - if this is not set then the default of WARNING will control
    logger.setLevel(logging.DEBUG)

    # Configure the logger handlers below, which indicate how to output log messages if they pass through the logger.

    # Configure the log file handler.
    if logfile_name is not None:
        # Use mode 'w' to restart the log because default is append 'a'.
        log_file_handler = logging.FileHandler(str(logfile_name), mode='w')
        log_file_handler.setLevel(logfile_log_level)
        log_file_handler.setFormatter(log_formatter)
        logger.addHandler(log_file_handler)

        # Save the logfile as a module variable.
        #__logfile_handler = log_file_handler
        #__logfile_name = logfile_name

    # Configure the console handler, which defaults to stderr:
    # - console output defaults to WARNING and worse
    if console_log_level != logging.NOTSET:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(console_log_level)
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

    # Print some messages to logging so that the application, user, etc. are known.
    if app_name is None:
        logger.info("Application = unknown")
    else:
        logger.info("Application = " + app_name)
    logger.info("Date/time = " + str(datetime.datetime.now()))
    logger.info("User = " + getpass.getuser())
    logger.info("Machine = " + platform.node())
    logger.info("Folder = " + os.getcwd())

    return logger