import sys
from azure.ai.ml.entities import Environment, BuildContext
from workflowhelperfunc.workflowhelper import initialize_mlclient
import ruamel.yaml
import json

ml_client = initialize_mlclient()

def get_environment(ml_client, env_name):
    env_list = ml_client.environments.list()
    for env in env_list:
        if env.name == env_name:
            return env
    return None

def flatten_dependencies(dependencies):
    flat_dependencies = []
    for dep in dependencies:
        if isinstance(dep, str):
            flat_dependencies.append(dep)
        elif isinstance(dep, dict):
            for key, values in dep.items():
                flat_dependencies.append(key)
                flat_dependencies.extend(values)
    return flat_dependencies

def environment_exists_and_same_version(ml_client, env_config):
    existing_env = get_environment(ml_client, env_config['name'])
    if existing_env and existing_env.latest_version == env_config['version']:
        print(f"Environment {existing_env.name} with version {existing_env.latest_version} already exists in AML.")
        conda_env_dependencies = flatten_dependencies(existing_env.conda_file.get('dependencies'))
        json_env_dependencies = flatten_dependencies(env_config.get('dependencies'))
        if conda_env_dependencies == json_env_dependencies:
            print("Conda dependencies in AML and JSON config are the same.")
        else:
            print("Conda dependencies in AML and JSON config are different.")
        return True
    return False

def environment_exists_and_auto_version(ml_client, env_config):
    existing_env = get_environment(ml_client, env_config['name'])
    if existing_env and env_config['version'] == 'auto':
        print(f"Environment {existing_env.name} with version {existing_env.latest_version} and set to 'auto' exists in AML.")
        conda_env_dependencies = flatten_dependencies(existing_env.conda_file.get('dependencies'))
        json_env_dependencies = flatten_dependencies(env_config.get('dependencies'))
        if conda_env_dependencies == json_env_dependencies:
            print("Conda dependencies in AML and JSON config are the same.")
        else:
            print("Conda dependencies in AML and JSON config are different, updating environment version in AML...")
            # update the version of the environment
            existing_env.version = str(int(existing_env.version) + 1)
            ml_client.environments.create_or_update(existing_env)
        return True
    return False


# get the JSON file path from command line arguments
json_file_path = sys.argv[1]

with open(json_file_path, 'r') as json_file:
    json_config = json.load(json_file)
    for env_config in json_config['conda']:
        if 'channels' in env_config and 'dependencies' in env_config:
            print(f"DEBUG: Processing environment {env_config['name']}...")
            if environment_exists_and_same_version(ml_client, env_config):
                continue
            elif environment_exists_and_auto_version(ml_client, env_config):
                continue
            else:
                print(f"Environment {env_config['name']} does not exist in AML, creating...")
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
                # create a new environment
                new_env = Environment(name=env_config['name'], version=env_config['version'] if env_config['version'] != 'auto' else '1', conda_file=conda_file_all)
                ml_client.environments.create_or_update(new_env)
