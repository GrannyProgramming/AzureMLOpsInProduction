import logging
import json
import os
import logging
from pathlib import Path
from jsonschema import validate, exceptions
import subprocess

def log_event(logger, level, event_message):
    """
    Function to log events at different levels.
    Parameters:
    logger: Logger object.
    level (str): Level of the logging event. Can be one of the following - 'debug', 'info', 'warning', 'error', 'critical'.
    event_message (str): Message to be logged.

    Returns: None
    """
    if level.lower() == 'debug':
        logger.debug(event_message)
    elif level.lower() == 'info':
        logger.info(event_message)
    elif level.lower() == 'warning':
        logger.warning(event_message)
    elif level.lower() == 'error':
        logger.error(event_message)
    elif level.lower() == 'critical':
        logger.critical(event_message)
    else:
        raise ValueError(f'Invalid log level: {level}')

def setup_logger(name):
    """
    Function to set up a logger.
    Parameters:
    name (str): Name of the logger.

    Returns: Logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Create a console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)

    # Create a file handler
    file_handler = logging.FileHandler('logfile.log')
    file_handler.setLevel(logging.DEBUG)

    # Create a formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    # Add the handlers to the logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


def load_and_set_env_vars(file_path=None, var_list=None):
    env_vars = {}

    # Load from file
    if file_path:
        with open(file_path, 'r') as f:
            env_vars.update(json.load(f))

    # Load from args
    if var_list:
        env_vars.update(dict(var.split("=") for var in var_list))
    
    # Set env vars
    for key, value in env_vars.items():
        env_var = f"{key.upper()}={value}"
        print(f"Setting environment variable {env_var}")
        os.system(f"echo {env_var} >> $GITHUB_ENV")

def load_config(config_file):
    with open(config_file, "r") as f:
        return json.load(f)