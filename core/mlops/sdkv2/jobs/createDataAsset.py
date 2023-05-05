from azure.ai.ml import MLClient
from azure.ai.ml.entities import Data
from azure.ai.ml.constants import AssetTypes
from azure.identity import DefaultAzureCredential
import time

# set VERSION variable
VERSION=time.strftime("%Y.%m.%d.%H%M%S", time.gmtime())

# These will be defined in the GH workflow. Test in notebook in AML, working.
# # Update with your details...
# subscription_id = "<SUBSCRIPTION_ID>"
# resource_group = "<RESOURCE_GROUP>"
# workspace = "<AML_WORKSPACE_NAME>"

# connect to the AzureML workspace
# NOTE: the subscription_id, resource_group, workspace variables are set 
# in the previous code snippet.
ml_client = MLClient(
    DefaultAzureCredential(), subscription_id, resource_group, workspace
)

# create a Data object
# NOTE: this inforation should be set in a master JSON file to avoid hard-coded varibles 
my_data = Data(
    path="./dataScience/src/data",
    type=AssetTypes.MLTABLE,
    description="A random sample of NYC Green and Yellow Taxi Data between 2015-19.",
    name="green_yellow_taxi_data",
    version=VERSION,
)

ml_client.data.create_or_update(my_data)


#ex1 ---------------------------------------------------------[]
# import json
# from azure.ai.machinelearning import MLClient
# from azure.ai.machinelearning.entities import Dataset, Datastore
# from azure.ai.ml.constants import AssetTypes

# config_file = "test.json"

# # Map data types to their corresponding entity types
# data_types = {
#     AssetTypes.URI_FILE: Dataset,
#     AssetTypes.URI_FOLDER: Dataset,
#     AssetTypes.ML_TABLE: Dataset
# }

# with open(config_file, "r") as f:
#     config = json.load(f)

# # Create a MLClient object
# client = MLClient()

# for data_config in config["data"]:
#     data_type = data_config["type"].lower()
#     data_name = data_config["name"]

#     # Check if the data asset already exists
#     if client.get_data_asset(data_name) is not None:
#         print(f"{data_type.capitalize()} data asset '{data_name}' already exists.")
#         continue

#     # Create the data asset
#     if data_type in data_types:
#         data_entity = data_types[data_type](name=data_name, **data_config)
#         client.create_data_asset(data_entity)
#         print(f"{data_type.capitalize()} data asset '{data_name}' created.")
#     else:
#         print(f"{data_type.capitalize()} data type is not supported.")







#------------------------------------------------------------
# EXAMPLE 2
# import json
# from azure.ai.machinelearning import MLClient
# from azure.ai.machinelearning.entities import Dataset, Datastore
# from azure.ai.ml.constants import AssetTypes

# config_file = "test.json"

# # Map data types to their corresponding entity types
# data_types = {
#     "dataset": Dataset,
#     "datastore": Datastore
# }

# # Create a MLClient object
# client = MLClient()

# # Cache existing data assets to avoid making unnecessary API calls
# existing_assets = {asset.name: asset for asset in client.list_data_assets()}

# with open(config_file, "r") as f:
#     config = json.load(f)

# # Filter out unsupported data types
# data_configs = [
#     data_config for data_config in config["data"] if data_config["type"].lower() in AssetTypes
# ]

# for data_config in data_configs:
#     data_type = data_config["type"].lower()
#     data_name = data_config["name"]

#     # Check if the data asset already exists
#     if data_name in existing_assets:
#         print(f"{data_type.capitalize()} data asset '{data_name}' already exists.")
#         continue

#     # Create the data asset
#     if data_type in data_types:
#         data_entity = data_types[data_type](name=data_name, **data_config)
#         client.create_data_asset(data_entity)
#         print(f"{data_type.capitalize()} data asset '{data_name}' created.")
#     else:
#         print(f"{data_type.capitalize()} data type is not supported.")



# ----------------------------------------------------------------


# ex3
# import json
# from azure.ai.machinelearning import MLClient
# from azure.ai.machinelearning.entities import Dataset, Datastore
# from azure.ai.ml.constants import AssetTypes

# config_file = "test.json"

# # Map data types to their corresponding entity types
# data_types = {
#     "uri_file": Dataset,
#     "uri_folder": Dataset,
#     "mltable": Dataset
# }

# with open(config_file, "r") as f:
#     config = json.load(f)

# # Create a MLClient object
# client = MLClient()

# # Initialize a dictionary to cache the results of client.get_data_asset()
# existing_assets = {}

# # Loop over the data assets in the config file
# for data_config in config["data"]:
#     data_type = data_config["type"].lower()
#     data_name = data_config["name"]
    
#     # Check if the data asset already exists
#     if data_name in existing_assets:
#         print(f"{data_type.capitalize()} data asset '{data_name}' already exists.")
#         continue

#     existing_asset = client.get_data_asset(data_name)
#     if existing_asset is not None:
#         existing_assets[data_name] = existing_asset
#         print(f"{data_type.capitalize()} data asset '{data_name}' already exists.")
#         continue

#     # Create the data asset
#     if data_type in data_types:
#         data_entity = data_types[data_type](
#             name=data_name,
#             version="auto",
#             asset_type=AssetTypes.DATA,
#             **data_config
#         )
#         client.create_data_asset(data_entity)
#         print(f"{data_type.capitalize()} data asset '{data_name}' created with version {data_entity.version}.")
#         existing_assets[data_name] = data_entity
#     else:
#         print(f"{data_type.capitalize()} data type is not supported.")