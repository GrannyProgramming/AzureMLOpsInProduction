from azure.identity import DefaultAzureCredential
from azure.ai.ml import MLClient, load_compute
from azure.ai.ml.entities import AmlCompute, ComputeInstance, KubernetesCompute
import os
import json 
import subprocess
from workflowhelperfunc.workflowhelper import validate_config


def get_cluster_id(compute_name, resource_group):
    get_cluster_id_command = f"az aks show --name {compute_name} --resource-group {resource_group} --query id -o tsv"
    id_process = subprocess.run(get_cluster_id_command, shell=True, check=True, text=True, capture_output=True)
    return id_process.stdout.strip()


def get_env_variables():
    return os.environ['ENVIRONMENT'], os.environ['SUBSCRIPTION_ID'], os.environ['WORKSPACE_NAME'], os.environ['RESOURCE_GROUP']


def get_directory_structure():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.join(script_dir, '..', '..')
    return script_dir, root_dir


def get_config_and_schema_files(root_dir, environment):
    config_file = os.path.join(root_dir, "variables", f'{environment}', "compute", "compute.json")
    schema_file = os.path.join(root_dir, "variables", f'{environment}', "compute", "computeSchema.json")
    return config_file, schema_file


def load_config(config_file):
    with open(config_file, "r") as f:
        return json.load(f)


def handle_existing_compute(compute_type, compute_name, client, resource_group):
    try:
        if compute_type == 'kubernetes' and client.compute.get(compute_name) is not None:
            cluster_id = get_cluster_id(compute_name, resource_group)
            print(f"{compute_type.capitalize()} compute '{compute_name}' already exists. ID: {cluster_id}")
            return True
        elif client.compute.get(compute_name) is not None:
            print(f"{compute_type.capitalize()} compute '{compute_name}' already exists.")
            return True
    except Exception as e:
        print(f"Error occurred: {e}")
        return False
    return False


def create_kubernetes_cluster(compute_name, resource_group):
    create_cluster_command = f"az aks create --resource-group {resource_group} --name {compute_name} --node-count 1 --enable-addons monitoring --generate-ssh-keys"
    subprocess.run(create_cluster_command, shell=True)
    cluster_id = get_cluster_id(compute_name, resource_group)
    print(f"Kubernetes cluster '{compute_name}' resource ID: {cluster_id}")
    return cluster_id


def main():
    environment, subscription_id, workspace_name, resource_group = get_env_variables()
    script_dir, root_dir = get_directory_structure()
    config_file, schema_file = get_config_and_schema_files(root_dir, environment)
    validate_config(config_file, schema_file)
    config = load_config(config_file)

    credential = DefaultAzureCredential()
    client = MLClient(credential=credential, subscription_id=f'{subscription_id}', workspace_name=f'{workspace_name}', resource_group_name=f'{resource_group}')
    
    compute_types = {
        "amlcompute": AmlCompute,
        "computeinstance": ComputeInstance,
        "kubernetes": KubernetesCompute
    }

    for compute_config in config["computes"]:
        compute_type = compute_config.pop("type").lower()
        compute_name = compute_config.pop("name")

        if handle_existing_compute(compute_type, compute_name, client, resource_group):
            continue

        if compute_type == "kubernetes":
            cluster_id = create_kubernetes_cluster(compute_name, resource_group)
            # compute_params = [
            #     {"name": f'{compute_name}'},
            #     {"type": f'{compute_type}'},
            #     { 
            #         "resource_id": f'{cluster_id}'
            #     },
            # ]
            k8s_compute = compute_types[compute_type](name=compute_name, resource_id=cluster_id)
            client.begin_create_or_update(k8s_compute)
            print(f"{compute_type.capitalize()} compute '{compute_name}' has been created.")

        elif compute_type in compute_types:
            compute = compute_types[compute_type](name=compute_name, **compute_config)
            client.compute.begin_create_or_update(compute)
            print(f"{compute_type.capitalize()} compute '{compute_name}' has been created.")


if __name__ == "__main__":
    main()
