# 1. Import the required libraries
import json
import os
import sys
from azure.ai.ml.entities import Environment
from azure.ai.ml import MlClient
from workflowhelperfunc.workflowhelper import initialize_mlclient

# 2. Configure workspace details and get a handle to the workspace
print("DEBUG: Initializing ml client...")
ml_client = initialize_mlclient()

# Helper function to check if an environment exists and create or update it if necessary
def create_environment_from_json(env_config):
    # Check if environment exists
    env_name = env_config["name"]
    env_version = env_config["version"]
    conda_file_all = env_config["dependencies"]
    env = None

    if Environment.exists(ml_client, env_name):
        env = Environment.get(ml_client, env_name)
        if env.version != env_version:
            print(f"The version for {env_name} defined in the JSON file doesn't match with the one in AML environment.")
        else:
            print(f"The environment {env_name} with version {env_version} already exists in AML.")
    else:
        env = Environment(ml_client, env_name)

    # Check if the conda files match
    if env.conda_file != conda_file_all:
        print(f"The conda file for {env_name} defined in the JSON file doesn't match with the one in AML environment.")
        if env_version == "auto":
            # Auto-increment version
            if env.version is None:
                env.version = "1"
            else:
                env.version = str(int(env.version) + 1)
            env.conda_file = conda_file_all
            print(f"The conda file for {env_name} has been updated to version {env.version} in AML environment.")
        else:
            env.conda_file = conda_file_all
            print(f"The conda file for {env_name} has been updated to the specified version in the JSON file.")
    else:
        print(f"The conda file for {env_name} matches with the one in AML environment.")

    env.save()

# 4. Load the environment configuration from a JSON file
with open(sys.argv[1], 'r') as json_file:
    data = json.load(json_file)

# 5. Create environments for each item in the JSON configuration
for env_config in data["conda"]:
    create_environment_from_json(env_config)
