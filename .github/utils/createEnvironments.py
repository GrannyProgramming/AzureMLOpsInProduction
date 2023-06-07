# 1. Import the required libraries
import json
import yaml
import sys
import os
from azure.ai.ml.entities import Environment, BuildContext
from workflowhelperfunc.workflowhelper import initialize_mlclient

# 2. Configure workspace details and get a handle to the workspace
print("DEBUG: Initializing ml client...")
ml_client = initialize_mlclient()

# 3. Define the function that creates environments according to their types specified in the JSON configuration
import tempfile
import shutil

def create_environment_from_json(env_config):
    # Get the existing environments with the given name
    existing_envs = list(ml_client.environments.list(env_config['name']))
    conda_file_all = env_config['dependencies']

    # Create a temporary file to hold the conda dependencies
    # Create a temporary file to hold the conda dependencies
    with tempfile.NamedTemporaryFile(suffix='.yml', delete=False, mode='w') as tmp_file:
        conda_file_path = tmp_file.name
        yaml.dump({'dependencies': conda_file_all}, tmp_file)

    try:
        # Case 1: Environment doesn't exist
        if len(existing_envs) == 0:
            print(f"Creating new environment: {env_config['name']}")

            if env_config['version'].lower() == 'auto':
                version = '1'
            else:
                version = env_config['version']

            new_env = Environment(name=env_config['name'], version=version, conda_file=conda_file_path)
            ml_client.environments.create_or_update(new_env)

        else:
            for existing_env in existing_envs:
                # Case 2: Environment exists with a given version
                if existing_env.version == env_config['version']:
                    print(f"Environment {env_config['name']} already exists with version {env_config['version']}")

                # Case 3: Environment exists, version is 'auto', and conda_file differs
                elif env_config['version'].lower() == 'auto' and existing_env.conda_file != conda_file_path:
                    print(f"Updating environment {env_config['name']} due to conda file mismatch.")

                    new_version = str(int(existing_env.version) + 1)  # increment version
                    updated_env = Environment(name=env_config['name'], version=new_version, conda_file=conda_file_path)
                    ml_client.environments.create_or_update(updated_env)

                else:
                    print(f"No action needed for environment {env_config['name']} with version {env_config['version']}")

    finally:
        # Delete the temporary file
        os.unlink(conda_file_path)

# 4. Load the environment configuration from a JSON file
with open(sys.argv[1], 'r') as json_file:
    data = json.load(json_file)

# 5. Create environments for each item in the JSON configuration
for env_config in data["conda"]:
    create_environment_from_json(env_config)
