from azure.identity import DefaultAzureCredential
from azure.ai.ml import MLClient
from azure.ai.ml.entities import AmlCompute, ComputeInstance, KubernetesCompute
import os
import json 
from workflowhelperfunc.workflowhelper import validate_config

# Retrieve environment variables
ENVIRONMENT = os.environ['ENVIRONMENT']
SUBSCRIPTION_ID = os.environ['SUBSCRIPTION_ID']
WORKSPACE_NAME = os.environ['WORKSPACE_NAME']
RESOURCE_GROUP = os.environ['RESOURCE_GROUP']

# Authenticate the client using the DefaultAzureCredential object
credential = DefaultAzureCredential()

# Define the directory of the current script and the root directory of the project
script_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.join(script_dir, '..', '..')

# Define the path to the configuration file and the schema file
config_file = os.path.join(root_dir, "variables", f'{ENVIRONMENT}', "compute", "compute.json")
schema_file = os.path.join(root_dir, "variables", f'{ENVIRONMENT}', "compute", "computeSchema.json")

# Validate the configuration file against the schema
validate_config(config_file, schema_file)

# Define a dictionary that maps compute types to their corresponding Azure classes
compute_types = {
    "amlcompute": AmlCompute,
    "computeinstance": ComputeInstance,
    "kubernetescompute": KubernetesCompute
}

# Load the compute configurations from the config file
with open(config_file, "r") as f:
    config = json.load(f)

# Create a MLClient object with the authenticated credential
client = MLClient(credential=credential, subscription_id=f'{SUBSCRIPTION_ID}', workspace_name=f'{WORKSPACE_NAME}', resource_group_name=f'{RESOURCE_GROUP}')

# Loop through each compute configuration
for compute_config in config["computes"]:
    # Extract the compute type and name from the configuration
    compute_type = compute_config.get("type").lower()
    compute_name = compute_config.get("name")

    # Try to get the compute from the Azure ML service
    try:
        if client.compute.get(compute_name) is not None:
            # If the compute already exists, print a message and move to the next configuration
            print(f"{compute_type.capitalize()} compute '{compute_name}' already exists.")
            continue
    except Exception as e:
        # If an exception is raised, it likely means the compute does not exist
        pass

    # If the compute type is recognized, create a new compute
    if compute_type in compute_types:
        # Remove the 'name' key from the compute_config dictionary
        compute_name = compute_config.pop("name")
         
        # Create a new compute instance with the specified name and configuration
        compute = compute_types[compute_type](name=compute_name, **compute_config)

        # Begin creating or updating the compute in the Azure ML service
        client.compute.begin_create_or_update(compute)

        # Print a message indicating that the compute has been created
        print(f"{compute_type.capitalize()} compute '{compute_name}' has been created.")
