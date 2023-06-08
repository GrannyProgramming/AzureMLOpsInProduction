import json
import sys
from azure.ai.ml.entities import Environment, BuildContext
from workflowhelperfunc.workflowhelper import initialize_mlclient
import ruamel.yaml

# Configure workspace details and get a handle to the workspace
print("DEBUG: Initializing ml client...")
ml_client = initialize_mlclient()

def get_env_name_without_version(name_with_version):
    if ':' in name_with_version:
        return name_with_version.split(':')[0]
    return name_with_version

def deep_equal(a, b):
    if type(a) != type(b):
        return False
    if isinstance(a, dict):
        if len(a) != len(b):
            return False
        for key in a:
            if key not in b or not deep_equal(a[key], b[key]):
                return False
    elif isinstance(a, list):
        if len(a) != len(b):
            return False
        # For 'pip' dependencies, use sets for comparison
        if all(isinstance(item, dict) for item in a) and all('pip' in item for item in a):
            a_pip_deps = set(a[0]['pip'])  # Assuming only one 'pip' item in the list
            b_pip_deps = set(b[0]['pip'])  # Assuming only one 'pip' item in the list
            return a_pip_deps == b_pip_deps
        # For other dependencies, use sets for comparison
        else:
            return set(a) == set(b)
    else:
        return a == b
    return True


# Define the function that creates environments according to their types specified in the JSON configuration
def create_environment_from_json(env_config):
    new_version = '1'
    print(f"DEBUG: Environment configuration: {env_config}")

    print("DEBUG: Checking if environment exists...")
    existing_envs = list(ml_client.environments.list(env_config['name']))
    existing_env = None
    if existing_envs:
        existing_envs_sorted = sorted(existing_envs, key=lambda e: int(e.version.split(':')[-1] if ':' in e.version else e.version), reverse=True)
        existing_env = existing_envs_sorted[0]
        print(f"DEBUG: Existing environment:")
    else:
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

        if existing_env:
            existing_conda_data = existing_env.validate() if existing_env else None

            if existing_conda_data is not None and 'dependencies' in existing_conda_data:
                if deep_equal(conda_dependencies['dependencies'], existing_conda_data['dependencies']):
                    print(f"The conda dependencies for {env_config['name']} match the existing ones.")
                    return False
                else:
                    print(f"The conda dependencies for {env_config['name']} do not match the existing ones.")
                    if env_config['version'] == 'auto':
                        new_version = str(int(existing_env.version.split(':')[-1] if ':' in existing_env.version else existing_env.version) + 1)
                        env = Environment(
                            image=existing_env.image,
                            name=get_env_name_without_version(existing_env.name),
                            version=new_version,
                            conda_file=conda_file_all,
                        )
                    else:
                        env = Environment(
                            image=existing_env.image,
                            name=get_env_name_without_version(existing_env.name),
                            version=env_config['version'],
                            conda_file=conda_file_all,
                        )
            else:
                new_version = str(int(existing_env.version.split(':')[-1] if ':' in existing_env.version else existing_env.version) + 1) if env_config['version'] == 'auto' else env_config['version']
                env = Environment(
                    image=existing_env.image,
                    name=get_env_name_without_version(existing_env.name),
                    version=new_version,
                    conda_file=conda_file_all,
                )
            if env is not None:
                ml_client.environments.create_or_update(env)
        else:
            new_version = '1'
            env = Environment(
                name=env_config['name'],
                version=new_version,
                conda_file=conda_file_all,
            )
            ml_client.environments.create_or_update(env)

def main(argv):
    with open(argv[1]) as f:
        env_config = json.load(f)
    create_environment_from_json(env_config)

if __name__ == "__main__":
    main(sys.argv)