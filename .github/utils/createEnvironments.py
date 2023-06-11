import json
import sys
from azure.ai.ml.entities import Environment
from workflowhelperfunc.workflowhelper import initialize_mlclient
import ruamel.yaml

def create_yaml_file(filename, content):
    with open(filename, 'w') as file:
        yaml = ruamel.yaml.YAML()
        yaml.indent(mapping=2, sequence=4, offset=2)
        yaml.dump(content, file)

def prepare_env_config(config, new_version):
    return {
        'image': config['image'],  
        'name': config['name'],
        'version': new_version,
        'conda_file': config['name'] + '.yml',
    }

def get_pip_deps(conda_deps):
    for dep in conda_deps:
        if isinstance(dep, dict) and 'pip' in dep:
            return dep['pip']
    return None

existing_deps = get_pip_deps(existing_env.conda_file.get('dependencies')) if existing_env else None

def create_or_update_environment(ml_client, env_config):
    conda_dependencies = {
        'name': env_config['name'],
        'channels': env_config['channels'],
        'dependencies': env_config['dependencies']
    }

    create_yaml_file(env_config['name'] + '.yml', conda_dependencies)

    existing_env = next((env for env in ml_client.environments.list() if env.name == env_config['name']), None)

    if existing_env:
        existing_env = ml_client.environments.get(name=existing_env.name, version=existing_env.latest_version)
        existing_deps = existing_env.conda_file.get('dependencies') if existing_env else None

        if existing_deps and existing_deps == env_config['dependencies']:
            print(f"The conda dependencies for {env_config['name']} match the existing ones.")
            return

        new_version = str(int(existing_env.version.split(':')[-1]) + 1) if env_config['version'] == 'auto' else env_config['version']
    else:
        new_version = '1'

    env = Environment(**prepare_env_config(env_config, new_version))
    ml_client.environments.create_or_update(env)


def main():
    if len(sys.argv) < 2:
        print('No configuration file provided.')
        sys.exit(1)

    print(f"DEBUG: Reading configuration file: {sys.argv[1]}")
    print("DEBUG: Initializing ml client...")
    ml_client = initialize_mlclient()

    with open(sys.argv[1], 'r') as f:
        config = json.load(f)

    for env_config in config['conda']:
        create_or_update_environment(ml_client, env_config)

if __name__ == '__main__':
    main()
