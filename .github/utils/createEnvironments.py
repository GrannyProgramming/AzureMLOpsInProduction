# 1. Import the required libraries
import json
import yaml
import logging
import sys
from azure.ai.ml.entities import Environment, BuildContext
from workflowhelperfunc.workflowhelper import initialize_mlclient

# 2. Configure workspace details and get a handle to the workspace
ml_client = initialize_mlclient()

# Set up logging
logging.basicConfig(level=logging.INFO)

# 3. Define the function that creates environments according to their types specified in the JSON configuration
def create_environment_from_json(env_config):
    try:
        # Try to get the specific environment version
        env = ml_client.environments.get(name=env_config['name'], version=env_config.get('version'))
        logging.info(f"Environment {env_config['name']} with version {env_config.get('version')} already exists. Skipping...")
    except Exception as e:  # Catch any exception
        logging.error(f"An error occurred: {e}")
        # If the environment doesn't exist, create it
        if 'image' in env_config:
            env = Environment(
                name=env_config['name'],
                version=env_config.get('version'),
                description=env_config.get('description'),
                image=env_config['image'],
            )
            ml_client.environments.create_or_update(env)

        elif 'path' in env_config:
            env = Environment(
                name=env_config['name'],
                version=env_config['version'],
                build=BuildContext(path=env_config['path']),
            )
            ml_client.environments.create_or_update(env)

        elif 'channels' in env_config and 'dependencies' in env_config:
            conda_dependencies = {
                'channels': env_config['channels'],
                'dependencies': env_config['dependencies']
            }

            conda_file = env_config['name'] + '.yml'
            with open(conda_file, 'w') as file:
                documents = yaml.dump(conda_dependencies, file)
            
            env = Environment(
                name=env_config['name'],
                version=env_config['version'],
                conda_file=documents,
            )
            ml_client.environments.create_or_update(env)
            
# Check if the script is invoked with necessary arguments
if len(sys.argv) < 2:
    logging.error('No configuration file provided.')
    sys.exit(1)

# Extract config file path
config_file_path = sys.argv[1]

# 4. Read the JSON configuration file and call the function defined in step 3 to create the environments
with open(config_file_path, 'r') as f:
    config = json.load(f)

for env_config in config['environments']:
    create_environment_from_json(env_config)
