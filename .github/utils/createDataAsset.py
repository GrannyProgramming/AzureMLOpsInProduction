import json
import sys
from azure.ai.ml import MLClient
from azure.ai.ml.entities import Data
from azure.ai.ml.constants import AssetTypes
from workflowhelperfunc.workflowhelper import setup_logger, log_event


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
        self.client = MLClient()
        self.existing_assets = {}

        self.logger = setup_logger(__name__)

    def load_config(self):
        """
        Load the configuration file.

        Returns
        -------
        dict
            Configuration data loaded from the file.
        """
        with open(self.config_file, "r") as f:
            return json.load(f)

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

        existing_asset = self.client.get_data_asset(data_name)
        if existing_asset is not None:
            self.existing_assets[data_name] = existing_asset
            return True

        return False

    def create_data_asset(self, data_config):
        """
        Create a data asset if it doesn't exist.

        Parameters
        ----------
        data_config : dict
            Configuration data for the data asset.
        """
        data_types = {
            "uri_file": Data,
            "uri_folder": Data,
            "mltable": Data
        }

        data_type = data_config["type"].lower()
        data_name = data_config["name"]

        if self.check_asset_exists(data_name):
            log_event(self.logger, 'info', f"{data_type.capitalize()} data asset '{data_name}' already exists.")
            return

        if data_type in data_types:
            data_entity = data_types[data_type](
                name=data_name,
                version="auto",
                asset_type=AssetTypes.Data,
                **data_config
            )
            self.client.create_data_asset(data_entity)
            log_event(self.logger, 'info', f"{data_type.capitalize()} data asset '{data_name}' created with version {data_entity.version}.")
            self.existing_assets[data_name] = data_entity
        else:
            log_event(self.logger, 'error', f"{data_type.capitalize()} data type is not supported.")

    def execute(self):
        """
        Main method to run the program.

        Load the configuration and create data assets based on the configuration.
        """
        config = self.load_config()

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