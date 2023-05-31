import json
from azure.ai.machinelearning import MLClient
from azure.ai.machinelearning.entities import Dataset, Datastore
from azure.ai.ml.constants import AssetTypes

config_file = "test.json"

# Map data types to their corresponding entity types
data_types = {
    "uri_file": Dataset,
    "uri_folder": Dataset,
    "mltable": Dataset
}

with open(config_file, "r") as f:
    config = json.load(f)

# Create a MLClient object
client = MLClient()

# Initialize a dictionary to cache the results of client.get_data_asset()
existing_assets = {}

# Loop over the data assets in the config file
for data_config in config["data"]:
    data_type = data_config["type"].lower()
    data_name = data_config["name"]
    
    # Check if the data asset already exists
    if data_name in existing_assets:
        print(f"{data_type.capitalize()} data asset '{data_name}' already exists.")
        continue

    existing_asset = client.get_data_asset(data_name)
    if existing_asset is not None:
        existing_assets[data_name] = existing_asset
        print(f"{data_type.capitalize()} data asset '{data_name}' already exists.")
        continue

    # Create the data asset
    if data_type in data_types:
        data_entity = data_types[data_type](
            name=data_name,
            version="auto",
            asset_type=AssetTypes.DATA,
            **data_config
        )
        client.create_data_asset(data_entity)
        print(f"{data_type.capitalize()} data asset '{data_name}' created with version {data_entity.version}.")
        existing_assets[data_name] = data_entity
    else:
        print(f"{data_type.capitalize()} data type is not supported.")