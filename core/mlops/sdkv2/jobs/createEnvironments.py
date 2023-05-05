from azure.ai.ml.entities import ComputeInstance, AmlCompute  
# Handle to the workspace
from azure.ai.ml import MLClient
import json
import yaml
import os
from azure.identity import DefaultAzureCredential, InteractiveBrowserCredential
from azure.ai.ml.entities import Environment, BuildContext
# Enter details of your AML workspace
subscription_id = "e62983d6-29cb-4435-b8d2-b19887c7a735"
resource_group = "clitesting"
workspace = "clitest-amcg"
AZURE_TENANT_ID = "16b3c013-d300-468d-ac64-7eda0820b6d3"
import tempfile
import yaml

if __name__ == "__main__":
    # credential = InteractiveBrowserCredential()
    ml_client = MLClient(
        DefaultAzureCredential(), subscription_id, resource_group, workspace
    )
    
    with open("environments.json", 'r') as f:
        buildEnv = json.load(f)

    for j, i in buildEnv.items():
        try:
            env = ml_client.environments.get(i['name'], i['version'])
            print(f"You already have an environment named {i['name']}, with version {i['version']}.")
        except:
            print("Creating a new AML environment...")
            myenv=i
            print(i)
            fd, path = tempfile.mkstemp(suffix=".yaml")
            try:
                with os.fdopen(fd, 'w') as tmp:
                    myfile=yaml.dump(myenv, tmp)
                    env_docker_conda = Environment(
                    image="mcr.microsoft.com/azureml/openmpi4.1.0-ubuntu20.04",
                    conda_file=path,
                    name=i['name'],
                    description="Environment created from a Docker image plus Conda environment.",
                    version=i['version']
                    )
                    ml_client.environments.create_or_update(env_docker_conda)
            finally:
                os.remove(path)
            print("YAML file saved.")


# ----------------------------------------------------
# ex 1 
# import json
# from azure.identity import DefaultAzureCredential
# from azure.ai.ml import MLClient
# from azure.ai.ml.entities import Environment
# from logging_config import setup_logging

# # Set up logging configuration
# setup_logging()

# ml_client = MLClient()

# # Authenticate to the workspace using mlclient
# credential = DefaultAzureCredential()
# workspace = ml_client.get_workspace()

# # Load the environment configuration from a JSON file
# with open('environment.json', 'r') as f:
#     env_configs = json.load(f)['environments']

# # Check if each environment already exists and create it if it does not
# for env_config in env_configs:
#     env_name = env_config['name']
#     env_version = env_config['version']
#     env = Environment.get(workspace, name=env_name, version=env_version)
#     if env is None:
#         env = Environment.from_dict(env_config)
#         env.register(workspace)
# my_env.python.conda_dependencies.add_pip_package('path/to/my_package-0.1.0-py3-none-any.whl')
#         logging.info(f"Created environment '{env_name}' with version '{env_version}'")
#     else:
#         logging.info(f"Environment '{env_name}' with version '{env_version}' already exists")
