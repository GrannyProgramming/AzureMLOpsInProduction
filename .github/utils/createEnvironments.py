# 1. Import the required libraries
import json
import yaml
import logging
import sys
from azure.ai.ml.entities import Environment, BuildContext
from workflowhelperfunc.workflowhelper import initialize_mlclient

# 2. Configure workspace details and get a handle to the workspace
ml_client = initialize_mlclient()

# 3. Define the function that creates environments according to their types specified in the JSON configuration
def create_environment_from_json(env_config):
    # Check if environment already exists with the same version
    existing_env = ml_client.environments.get(name=env_config['name'], version=env_config.get('version'))
    if existing_env:
        logging.info(f"Environment {env_config['name']} with version {env_config.get('version')} already exists. Skipping...")
        return

    # if 'image' in env_config:
        # env = Environment(
        #     name=env_config['name'],
        #     version=env_config.get('version'),
        #     description=env_config.get('description'),
        #     image=env_config['image'],
        # )
        # ml_client.environments.create_or_update(env)

    if 'build' in env_config:
        env = Environment(
            name=env_config['name'],
            build=BuildContext(path=env_config['build']),
            description=env_config.get('description')
        )
        ml_client.environments.create_or_update(env)

    elif 'channels' in env_config and 'dependencies' in env_config:
        conda_dependencies = {
            'name': env_config['name'],
            'channels': env_config['channels'],
            'dependencies': env_config['dependencies']
        }

        conda_file_all = env_config['name'] + '.yml'
        with open(conda_file_all, 'w') as file:
            conda_file = yaml.dump(conda_dependencies, file)
        
        env = Environment(
            image=env_config['image'],
            name=env_config['name'],
            version=env_config['version'],
            conda_file=conda_file,
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
