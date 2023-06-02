import json
from azure.ai.machinelearning import MLClient
from azure.ai.machinelearning.entities import Dataset, Datastore
from azure.ai.ml.constants import AssetTypes


class DataAssetManager:
    """
    A class to manage Azure ML data assets.

    Attributes
    ----------
    config_file : str
        Path to the configuration file.
    client : MLClient
        The Azure ML client.
    existing_assets : dict
        Dictionary to cache the results of client.get_data_asset().

    Methods
    -------
    load_config():
        Load the configuration file.
    check_asset_exists(data_name: str) -> bool:
        Check if the data asset already exists.
    create_data_asset(data_config: dict):
        Create a data asset if it doesn't exist.
    execute():
        Main method to run the program.
    """

    def __init__(self, config_file):
        """
        Parameters
        ----------
        config_file : str
            Path to the configuration file.
        """
        self.config_file = config_file
        self.client = MLClient()
        self.existing_assets = {}

    def load_config(self):
        """Load the configuration file."""
        with open(self.config_file, "r") as f:
            return json.load(f)

    def check_asset_exists(self, data_name):
        """Check if the data asset already exists."""
        if data_name in self.existing_assets:
            return True

        existing_asset = self.client.get_data_asset(data_name)
        if existing_asset is not None:
            self.existing_assets[data_name] = existing_asset
            return True

        return False

    def create_data_asset(self, data_config):
        """Create a data asset if it doesn't exist."""
        # Map data types to their corresponding entity types
        data_types = {
            "uri_file": Dataset,
            "uri_folder": Dataset,
            "mltable": Dataset
        }

        data_type = data_config["type"].lower()
        data_name = data_config["name"]

        if self.check_asset_exists(data_name):
            print(f"{data_type.capitalize()} data asset '{data_name}' already exists.")
            return

        if data_type in data_types:
            data_entity = data_types[data_type](
                name=data_name,
                version="auto",
                asset_type=AssetTypes.DATA,
                **data_config
            )
            self.client.create_data_asset(data_entity)
            print(f"{data_type.capitalize()} data asset '{data_name}' created with version {data_entity.version}.")
            self.existing_assets[data_name] = data_entity
        else:
            print(f"{data_type.capitalize()} data type is not supported.")

    def execute(self):
        """Main method to run the program."""
        config = self.load_config()

        # Loop over the data assets in the config file
        for data_config in config["data"]:
            self.create_data_asset(data_config)


if __name__ == "__main__":
    manager = DataAssetManager("test.json")
    manager.execute()
