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
def create_environment_from_json(env_config):
    new_version = '1'  # Initialize version
    print(f"DEBUG: Environment configuration: {env_config}")

    # Check if environment already exists
    print("DEBUG: Checking if environment exists...")
    existing_envs = list(ml_client.environments.list(env_config['name']))
    existing_env = None
    if existing_envs:
        # Sort by version number to get the latest version
        existing_envs_sorted = sorted(existing_envs, key=lambda e: int(e.version), reverse=True)
        existing_env = existing_envs_sorted[0]  # The latest version
        print(f"DEBUG: Existing environment:")
    else:  # No existing environment, create new one
        env_config['version'] = new_version if env_config['version'] == 'auto' else env_config['version']
        print(f"DEBUG: No existing environment found, creating new environment with version: {env_config['version']}")

    env = None
    if 'build' in env_config:
        # Build Context case
        # Create build context
        print("DEBUG: Creating build context...")

        # Ensure that the Docker context path is absolute
        docker_context_path = os.path.join(os.getenv("GITHUB_WORKSPACE", ""), env_config['build'])

        if not os.path.exists(docker_context_path):
            print(f"ERROR: Docker context path {docker_context_path} does not exist.")
            return

        build_context = BuildContext(path=docker_context_path)

        # Compare existing AML build context with new build context
        if existing_env and existing_env.build == build_context:
            print(f"The build context for {env_config['name']} matches the existing one.")
        else:
            print(f"The build context for {env_config['name']} does not match the existing one. Creating new environment...")
            env = Environment(
                name=env_config['name'],
                build=build_context,
                version=env_config['version'],
                description=env_config.get('description')
            )

    elif 'channels' in env_config and 'dependencies' in env_config:
        print("DEBUG: Creating environment with conda dependencies...")
        conda_dependencies = {
            'name': env_config['name'],
            'channels': env_config['channels'],
            'dependencies': env_config['dependencies']
        }

        conda_file_all = env_config['name'] + '.yml'
        with open(conda_file_all, 'w') as file:
            conda_file = yaml.dump(conda_dependencies, file)

        # For version set to 'auto', check existing environment conda file
        if existing_env and env_config['version'] == 'auto':
            # Get existing conda file dependencies
            existing_conda_data = existing_env.conda_file_all

            # Compare dependencies
            if conda_dependencies != existing_conda_data:
                print(f"The conda dependencies for {env_config['name']} do not match the existing ones.")
                # Increment version if dependencies do not match
                existing_env.version = str(int(existing_env.version) + 1)
                existing_env.conda_file_all = conda_file
                env = existing_env

    # If new environment created or updated, register it
    if env:
        print(f"DEBUG: Registering environment {env_config['name']} version {env_config['version']}")
        env = ml_client.environments.create_or_update(env)
    else:
        print(f"DEBUG: No changes to the environment {env_config['name']} detected")

# 4. Load the environment configuration from a JSON file
with open(sys.argv[1], 'r') as json_file:
    data = json.load(json_file)

# 5. Create environments for each item in the JSON configuration
for env_config in data:
    create_environment_from_json(env_config)
