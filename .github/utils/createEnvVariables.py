import os
import json

def set_environment_variables(file_path):
    """
    Set environment variables from a JSON file.

    Args:
        file_path (str): The path to the JSON file containing the variables.

    Raises:
        FileNotFoundError: If the specified file path does not exist.
        KeyError: If the specified JSON file does not contain all required variables.

    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found at {file_path}")

    # Read JSON file
    with open(file_path, 'r') as f:
        variables = json.load(f)

    # Set environment variables
    required_vars = ['subscription_id', 'resource_group', 'workspace']
    for var in required_vars:
        if var not in variables:
            raise KeyError(f"Missing required variable '{var}' in file '{file_path}'")
        os.environ[var.upper()] = variables[var]
