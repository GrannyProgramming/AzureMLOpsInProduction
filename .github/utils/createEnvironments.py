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
# Check if environment already exists
    new_version = '1'  # Add this line
    try:# Initialize version
        # Get all versions of the environment by name
        existing_envs = ml_client.environments.list(env_config['name'])
        existing_envs_get = ml_client.environments.get(env_config['name'])
        for env in existing_envs:
            print("DEBUG: existing_envs: ", env)
        print("DEBUG: existing_envs: ", existing_envs_get)

        if existing_envs:
            # Sort by version number to get the latest version
            existing_envs_sorted = sorted(existing_envs, key=lambda e: int(e.version), reverse=True)
            existing_env = existing_envs_sorted[0]  # The latest version
            
            if existing_env.conda_file == env_config.get('conda_file', '') and env_config['version'].lower() == 'auto':
                print(f"Environment with name {env_config['name']} and version {existing_env.version} already exists and dependencies are the same.")
                return
            elif env_config['version'].lower() != 'auto':
                print(f"Warning: SKIPPING ENVIRONMENT CREATION - Environment {env_config['name']} version and name are same but dependencies have changed. Version is not set to 'auto', so version will not be incremented.")
                return
            elif not existing_env.conda_file:
                print("Warning: The environment exists but there are no dependencies specified.")
                return
            else:
                print("Dependencies have changed or version is set to 'auto', incrementing version and updating environment.")
                new_version = str(int(existing_env.version) + 1)  # Increment the version number
        elif env_config['version'].lower() != 'auto':
            # If environment doesn't exist and version is not auto, set new version as given version
            new_version = env_config['version']

    except Exception as e:
        print(f"An error occurred: {str(e)}. Proceeding to creation/update...")                
    env = None
    if 'build' in env_config:
        env = Environment(
            name=env_config['name'],
            build=BuildContext(path=env_config['build']),
            version=new_version,
            description=env_config.get('description')
        )
    elif 'image' in env_config:
        env = Environment(
            name=env_config['name'],
            version=new_version,
            image=env_config['image'],
            description=env_config.get('description')
        )
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
            name=env_config['name'],
            version=new_version,
            conda_file=conda_file_all,
        )
        
    if env is not None:
        ml_client.environments.create_or_update(env)
    else:
        print(f"Invalid configuration for environment {env_config['name']}")

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
