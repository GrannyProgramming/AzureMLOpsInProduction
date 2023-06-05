# 1. Import the required libraries
import json
import yaml
import sys
from azure.ai.ml.entities import Environment, BuildContext
from workflowhelperfunc.workflowhelper import initialize_mlclient

# 2. Configure workspace details and get a handle to the workspace
ml_client = initialize_mlclient()

# 3. Define the function that creates environments according to their types specified in the JSON configuration
def create_environment_from_json(env_config):
    # Check if environment already exists with the same version
    try:
        existing_env = ml_client.environments.get(name=env_config['name'], version=env_config['version'])
        if existing_env:
            print(f"Environment with name {env_config['name']} and version {env_config['version']} already exists.")
            return
    except Exception as e:
        print("Environment does not exist or an error occurred while fetching it. Proceeding to creation/update...")



# Check if the script is invoked with necessary arguments
if len(sys.argv) < 2:
    print('No configuration file provided.')
    sys.exit(1)

# Extract config file path
config_file_path = sys.argv[1]

# 4. Read the JSON configuration file and call the function defined in step 3 to create the environments
with open(config_file_path, 'r') as f:
    config = json.load(f)

for env_config in config['environments']:
    create_environment_from_json(env_config)
