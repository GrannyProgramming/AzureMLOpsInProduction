import os
from azure.identity import DefaultAzureCredential
from azure.ai.ml import MLClient
from azure.ai.ml.entities import AmlCompute, ComputeInstance, KubernetesCompute
import json 

# Authenticate the client using the DefaultAzureCredential object
credential = DefaultAzureCredential()

config_file = os.path.join(os.getcwd(), "..", "..", "..", "variables", "compute", "compute.json")

compute_types = {
    "amlcompute": AmlCompute,
    "computeinstance": ComputeInstance,
    "kubernetescompute": KubernetesCompute
}

with open(config_file, "r") as f:
    config = json.load(f)

# Create a MLClient object with the authenticated credential
client = MLClient(credential=credential)

for compute_config in config["computes"]:
    compute_type = compute_config["type"].lower()
    compute_name = compute_config["name"]

    # Check if the compute already exists
    if client.get_compute(compute_name) is not None:
        print(f"{compute_type.capitalize()} compute '{compute_name}' already exists.")
        continue

    # Create the compute
    if compute_type in compute_types:
        compute = compute_types[compute_type](name=compute_name, **compute_config)
