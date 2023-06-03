import logging
import json
import os
import logging
from azure.ai.ml import MLClient
from azure.identity import DefaultAzureCredential

def log_event(logger, level, event_message):
    """Log events at different levels.

    Parameters
    ----------
    logger : Logger
        Logger object.
    level : str
        Level of the logging event. Can be 'debug', 'info', 'warning', 'error', 'critical'.
    event_message : str
        Message to be logged.

    Raises
    ------
    ValueError
        If the log level is invalid.
    """
    LOG_LEVELS = {'debug', 'info', 'warning', 'error', 'critical'}
    level = level.lower()

    if level not in LOG_LEVELS:
        raise ValueError(f'Invalid log level: {level}')

    getattr(logger, level)(event_message)

def setup_logger(name):
    """Set up and return a logger.

    If a logger with the given name already exists, the existing logger is returned.
    Otherwise, a new logger is created and returned.

    Parameters
    ----------
    name : str
        Name of the logger.

    Returns
    -------
    logger : Logger
        Logger object.
    """

    logger = logging.getLogger(name)
    if not logger.handlers:  # To prevent creating multiple handlers
        logger.setLevel(logging.DEBUG)  # Logger level

        # Create a console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)  # Handler level

        # Create a formatter and add it to the handler
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)

        # Add the handler to the logger
        logger.addHandler(console_handler)
    return logger


def load_and_set_env_vars(file_path=None, var_list=None):
    """Load and set environment variables from a file and/or a list.

    Parameters
    ----------
    file_path : str, optional
        Path to the JSON file containing environment variables.
    var_list : list of str, optional
        List of strings in the format "KEY=VALUE".

    Notes
    -----
    The environment variables are set in the format "KEY=VALUE".
    """
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
    """Load and return a configuration from a JSON file.

    Parameters
    ----------
    config_file : str
        Path to the JSON file containing the configuration.

    Returns
    -------
    config : dict
        Configuration loaded from the JSON file.
    """
    with open(config_file, "r") as f:
        return json.load(f)
    
def initialize_mlclient():
    """Initialize and return an MLClient object.

    This function uses the following environment variables:
    - SUBSCRIPTION_ID
    - RESOURCE_GROUP_NAME
    - WORKSPACE_NAME
    - AZURE_CLIENT_ID
    - AZURE_TENANT_ID
    - AZURE_CLIENT_SECRET

    Returns
    -------
    client : MLClient
        An initialized MLClient object.

    Raises
    ------
    ValueError
        If one or more environment variables are missing.
    """
    required_vars = ['SUBSCRIPTION_ID', 'RESOURCE_GROUP', 'WORKSPACE_NAME']

    if not all(os.getenv(var) for var in required_vars):
        raise ValueError("One or more environment variables are missing for MLClient.")

    subscription_id = os.getenv('SUBSCRIPTION_ID')
    resource_group_name = os.getenv('RESOURCE_GROUP')
    workspace_name = os.getenv('WORKSPACE_NAME')
    credential = DefaultAzureCredential()

    return MLClient(
        subscription_id=subscription_id,
        resource_group_name=resource_group_name,
        workspace_name=workspace_name,
        credential=credential
    )