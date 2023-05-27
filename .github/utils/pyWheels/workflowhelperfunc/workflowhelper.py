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

def load_env_vars_from_file(file_path):
    env_file = Path(file_path)
    with env_file.open() as f:
        return json.load(f)

def load_env_vars_from_args(var_list):
    env_vars = {}
    for var in var_list:
        key, value = var.split("=")
        env_vars[key] = value
    return env_vars

def set_env_vars(env_vars):
    for key, value in env_vars.items():
        env_var = f"{key.upper()}={value}"
        print(f"Setting environment variable {env_var}")
        os.system(f"echo {env_var} >> $GITHUB_ENV")

def load_and_set_env_vars(file_path=None, var_list=None):
    env_vars = {}

    if file_path:
        env_vars.update(load_env_vars_from_file(file_path))

    if var_list:
        env_vars.update(load_env_vars_from_args(var_list))

    set_env_vars(env_vars)

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