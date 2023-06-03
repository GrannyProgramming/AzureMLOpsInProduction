import sys
from azure.ai.ml.entities import Data
from azure.ai.ml.constants import AssetTypes
from workflowhelperfunc.workflowhelper import setup_logger, log_event, initialize_mlclient, load_config

class DataAssetManager:
    """Manage Azure ML Data Assets."""

    def __init__(self, config_file):
        """
        Initialize the DataAssetManager.

        Parameters
        ----------
        config_file : str
            Path to the configuration file.
        """
        self.config_file = config_file
        self.client = initialize_mlclient()
        self.existing_assets = {}

        self.logger = setup_logger(__name__)

    def check_asset_exists(self, data_name):
        """
        Check if the data asset already exists.

        Parameters
        ----------
        data_name : str
            Name of the data asset.

        Returns
        -------
        bool
            True if the data asset exists, False otherwise.
        """
        if data_name in self.existing_assets:
            return True

        existing_asset = self.client.data.get(data_name)
        if existing_asset is not None:
            self.existing_assets[data_name] = existing_asset
            return True

        return False

    def create_data_asset(self, data_config):
        """
        Create or update a data asset.

        Parameters
        ----------
        data_config : dict
            Configuration data for the data asset.
        """
        required_keys = ['type', 'name']
        if not all(key in data_config for key in required_keys):
            log_event(self.logger, 'error', f"Data config is missing required keys: {', '.join(required_keys)}.")
            return

        data_types = {
            "uri_file": AssetTypes.URI_FILE,
            "uri_folder": AssetTypes.URI_FOLDER,
            "mltable": AssetTypes.MLTABLE  
        }

        data_type = data_config["type"].lower()
        data_name = data_config["name"]

        if data_type not in data_types:
            log_event(self.logger, 'error', f"{data_type.capitalize()} data type is not supported.")
            return

        try:
            data_entity = Data(
                name=data_name,
                version="auto",
                type=data_types[data_type],
                description=data_config.get("description", ""),
                path=data_config.get("path", ""),
            )
            self.client.data.create_or_update(data_entity)
            log_event(self.logger, 'info', f"{data_type.capitalize()} data asset '{data_name}' created or updated with version {data_entity.version}.")
            self.existing_assets[data_name] = data_entity
        except Exception as e:
            log_event(self.logger, 'error', f"Failed to create or update {data_type.capitalize()} data asset '{data_name}': {str(e)}")

    def execute(self):
        """
        Main method to run the program.

        Load the configuration and create data assets based on the configuration.
        """
        config = load_config(self.config_file)

        for data_config in config["data"]:
            self.create_data_asset(data_config)

if __name__ == "__main__":
    """Main execution of the script: Initialize the DataAssetManager and execute it."""
    logger = setup_logger(__name__)

    try:
        config_file = sys.argv[1]
        manager = DataAssetManager(config_file)
        manager.execute()
    except Exception as e:
        log_event(logger, 'error', f"An error occurred: {str(e)}")