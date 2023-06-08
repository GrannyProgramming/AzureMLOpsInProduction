import json
import sys
from azure.ai.ml.entities import Environment, BuildContext
from workflowhelperfunc.workflowhelper import initialize_mlclient
import ruamel.yaml

# Configure workspace details and get a handle to the workspace
print("DEBUG: Initializing ml client...")
ml_client = initialize_mlclient()

# Define the function that creates environments according to their types specified in the JSON configuration
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
        build_context = BuildContext(path=env_config['build'])

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
            yaml = ruamel.yaml.YAML()
            yaml.indent(mapping=2, sequence=4, offset=2)
            yaml.dump(conda_dependencies, file)

        # For version set to 'auto', check existing environment conda file
        if existing_env:
            # Check if the versions are the same
            if env_config['version'] == existing_env.version:
                # Get existing conda file dependencies
                existing_conda_data = existing_env.validate().conda_file if existing_env.validate() else None

                # Compare dependencies
                if conda_dependencies == existing_conda_data:
                    print(f"The conda dependencies for {env_config['name']} match the existing ones.")
                    return False  # Return False as a signal to continue to the next environment
                else:
                    print(f"The conda dependencies for {env_config['name']} do not match the existing ones.")
            else:
                # Version is different, create new environment with new version
                env = Environment(
                    image=existing_env.image,
                    name=existing_env.name,
                    version=str(int(existing_env.version) + 1),
                    conda_file=conda_file_all,
                )
        else:
            # No existing environment, create new one
            env = Environment(
                image=env_config['image'],
                name=env_config['name'],
                version=env_config['version'],
                conda_file=conda_file_all,
            )

        if env is not None:
            ml_client.environments.create_or_update(env)
        else:
            print(f"Invalid configuration for environment {env_config['name']}")
        return True

# Check if the script is invoked with necessary arguments
if len(sys.argv) < 2:
    print('No configuration file provided.')
    sys.exit(1)

# Extract config file path
config_file_path = sys.argv[1]

# Read the JSON configuration file and call the function defined above to create the environments
print(f"DEBUG: Reading configuration file: {config_file_path}")
with open(config_file_path, 'r') as f:
    config = json.load(f)

for env_config in config['conda']:
    if not create_environment_from_json(env_config):  # if the function returns False, continue to the next environment
        continue
