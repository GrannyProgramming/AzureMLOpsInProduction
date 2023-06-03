import json
from azure.ai.ml.entities import Environment
from workflowhelperfunc.workflowhelper import setup_logger, log_event, initialize_mlclient


ml_client = initialize_mlclient()

# Authenticate to the workspace using mlclient
workspace = ml_client.get_workspace()

# Load the environment configuration from a JSON file
with open('environment.json', 'r') as f:
    env_configs = json.load(f)['environments']

# Check if each environment already exists and create it if it does not
for env_config in env_configs:
    env_name = env_config['name']
    env_version = env_config['version']
    env = Environment.get(workspace, name=env_name, version=env_version)
    if env is None:
        env = Environment.from_dict(env_config)
        env.register(workspace)
        # my_env.python.conda_dependencies.add_pip_package('path/to/my_package-0.1.0-py3-none-any.whl')
        # logging.info(f"Created environment '{env_name}' with version '{env_version}'")
    else:
        print(f"Environment '{env_name}' with version '{env_version}' already exists")
