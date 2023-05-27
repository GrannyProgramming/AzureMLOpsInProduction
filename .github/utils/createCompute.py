from azure.identity import DefaultAzureCredential
from azure.ai.ml import MLClient
from azure.ai.ml.entities import AmlCompute, ComputeInstance, KubernetesCompute
import os
import json 

ENVIRONMENT = os.environ['ENVIRONMENT']
SUBSCRIPTION_ID = os.environ['SUBSCRIPTION_ID']
WORKSPACE_NAME = os.environ['WORKSPACE_NAME']
RESOURCE_GROUP = os.environ['RESOURCE_GROUP']

# Authenticate the client using the DefaultAzureCredential object
credential = DefaultAzureCredential()
script_dir = os.path.dirname(os.path.abspath(__file__))  # directory of the current script
root_dir = os.path.join(script_dir, '..', '..')  # root directory of the project
config_file = os.path.join(root_dir, "variables", f'{ENVIRONMENT}', "compute", "compute.json")

compute_types = {
    "amlcompute": AmlCompute,
    "computeinstance": ComputeInstance,
    "kubernetescompute": KubernetesCompute
}

with open(config_file, "r") as f:
    config = json.load(f) 

# Create a MLClient object with the authenticated credential
client = MLClient(credential=credential, subscription_id=f'{SUBSCRIPTION_ID}', workspace_name=f'{WORKSPACE_NAME}', resource_group_name=f'{RESOURCE_GROUP}')
            
for compute_config in config["computes"]:
    compute_type = compute_config.pop("type").lower()
    compute_name = compute_config.pop("name")

    # Check if the compute already exists
    try:
        if client.compute.get(compute_name) is not None:
            print(f"{compute_type.capitalize()} compute '{compute_name}' already exists.")
            continue
    except Exception as e:
        # Exception would be raised if compute does not exist
        pass

    # Create the compute
    if compute_type in compute_types:
        # use **kwargs to handle optional parameters
        compute = compute_types[compute_type](name=compute_name, **compute_config)
        
        # Create the compute instance
        client.compute.begin_create_or_update(compute)
        print(f"{compute_type.capitalize()} compute '{compute_name}' has been created.")
