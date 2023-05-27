import logging
import json
import os
from pathlib import Path
from jsonschema import validate, exceptions


def setup_logging(log_file_path: str, level: str = "INFO") -> None:
    # Configure logging
    logging.basicConfig(
        filename=log_file_path,
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create a stream handler to output logs to the console
    console = logging.StreamHandler()
    console.setLevel(level)
    console.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logging.getLogger().addHandler(console)


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

def validate_config(config_path, schema_path):
    # Load the schema
    with open(schema_path, 'r') as file:
        schema = json.load(file)

    # Load the config file
    with open(config_path, 'r') as file:
        config = json.load(file)

    try:
        # Validate the config against the schema
        validate(instance=config, schema=schema)
        print("JSON config is valid.")
    except exceptions.ValidationError as e:
        print(f"JSON config is invalid: {e.message}")