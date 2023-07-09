import sys
from datetime import datetime
from azure.ai.ml.entities import Data
from azure.ai.ml.constants import AssetTypes
from workflowhelperfunc.workflowhelper import setup_logger, log_event, initialize_mlclient, load_config

# Check if the required keys are in the configuration
def check_required_keys(data_config, logger):
    required_keys = ['type', 'name']
    missing_keys = [key for key in required_keys if key not in data_config]
    if missing_keys:
        log_event(logger, 'error', f"Data config is missing required keys: {', '.join(missing_keys)}.")
        return False
    return True

# Check if the type of the data is supported
def check_data_type(data_config, logger):
    data_types = {
        "uri_file": AssetTypes.URI_FILE,
        "uri_folder": AssetTypes.URI_FOLDER,
        "mltable": AssetTypes.MLTABLE  
    }
    data_type = data_config["type"].lower()
    if data_type not in data_types:
        log_event(logger, 'error', f"{data_type.capitalize()} data type is not supported.")
        return None
    return data_types[data_type]

# Create or update the data asset
def create_or_update_asset(client, data_config, data_type, logger):
    data_name = data_config["name"]
    data_version = data_config.get('version', datetime.now().strftime('%Y%m%d'))
    try:
        data_entity = Data(
            name=data_name,
            version=data_version,
            type=data_type,
            description=data_config.get("description", ""),
            path=data_config.get("path", ""),
        )
        client.data.create_or_update(data_entity)
        log_event(logger, 'info', f"{data_config['type'].capitalize()} data asset '{data_name}' created or updated with version {data_entity.version}.")
        return data_entity
    except Exception as e:
        log_event(logger, 'error', f"Failed to create or update {data_config['type'].capitalize()} data asset '{data_name}': {str(e)}")
        return None

def create_data_asset(client, existing_assets, data_config, logger):
    if not check_required_keys(data_config, logger):
        return
    data_type = check_data_type(data_config, logger)
    if data_type is None:
        return
    data_entity = create_or_update_asset(client, data_config, data_type, logger)
    if data_entity is not None:
        existing_assets[data_config['name']] = data_entity

def execute(client, config_file, logger):
    config = load_config(config_file)
    existing_assets = {}

    for data_config in config["data"]:
        create_data_asset(client, existing_assets, data_config, logger)

def main(config_file):
    logger = setup_logger(__name__)

    try:
        client = initialize_mlclient()
        execute(client, config_file, logger)
    except Exception as e:
        log_event(logger, 'error', f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main(sys.argv[1])
