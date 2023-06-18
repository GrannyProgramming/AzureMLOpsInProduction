import json
import sys
from azure.ai.ml.entities import Environment, BuildContext
import ruamel.yaml as yaml
from workflowhelperfunc.workflowhelper import initialize_mlclient, setup_logger, log_event
from functools import wraps

class EnvironmentManager:
    """
    Class to manage Azure ML environments.
    """

    def __init__(self, ml_client, logger) -> None:
        """
        Initialize the manager with an Azure ML client and a logger.

        Args:
            ml_client : Azure ML client object.
            logger : Logger object.
        """
        self.ml_client = ml_client
        self.logger = logger

    @staticmethod
    def catch_exception(func):
        """
        A decorator that wraps a function to catch and log any exceptions that occur 
        during the execution of the function.

        Args:
            func (function): The function to be wrapped.

        Returns:
            function: The wrapped function.
        """
        @wraps(func)
        def inner(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                args[0].logger.error(f"Failed to execute function: {func.__name__}. Error: {e}")
                raise
        return inner

    @catch_exception
    def create_yaml_file(self, filename: str, content: dict) -> None:
        """
        Creates a YAML file with the given content.

        Args:
            filename : Name of the file to be created.
            content : Content to be written to the file.
        """
        with open(filename, 'w') as file:
            yaml_handler = yaml.YAML()
            yaml_handler.indent(mapping=2, sequence=4, offset=2)
            yaml_handler.dump(content, file)

    @staticmethod
    def prepare_env_config(config: dict, new_version: str) -> dict:
        """
        Prepares the environment configuration.

        Args:
            config : The configuration details.
            new_version : The new version of the environment.

        Returns:
            dict: The prepared configuration.
        """
        env_config = {
            'image': config['image'],
            'name': config['name'],
            'version': new_version,
            'conda_file': f"{config['name']}.yml",
        }
        return env_config

    @catch_exception
    def create_or_update_environment(self, env_config: dict) -> None:
        """
        Creates or updates an Azure ML environment based on provided configuration.

        Args:
            env_config : The configuration details.
        """
        conda_dependencies = {
            'name': env_config['name'],
            'channels': env_config['channels'],
            'dependencies': env_config['dependencies']
        }

        self.create_yaml_file(f"{env_config['name']}.yml", conda_dependencies)

        existing_env = next((env for env in self.ml_client.environments.list() 
                            if env.name == env_config['name']), None)

        if existing_env:
            existing_env = self.ml_client.environments.get(name=existing_env.name, 
                                                         version=existing_env.latest_version)
            existing_deps = existing_env.conda_file.get('dependencies') if existing_env else None

            if existing_deps == env_config['dependencies']:
                self.logger.info(f"As the conda dependencies for {env_config['name']} match the existing ones. Environment was not updated.")
                return

            new_version = str(int(existing_env.version) + 1) if env_config['version'] == "auto" else env_config['version']

            if new_version == existing_env.version:
                self.logger.info(f"Environment '{env_config['name']}' with version {new_version} has different dependencies. However environment version is less than equal to the JSON config. Update the environment version in the JSON to proceed with the update. Environment not updated.")
                return

            self.logger.info(f"Updating the environment {env_config['name']}.")
        else:
            new_version = '1'
            self.logger.info(f"Creating new environment {env_config['name']}.")

        env = Environment(**self.prepare_env_config(env_config, new_version))
        self.ml_client.environments.create_or_update(env)
        self.logger.info(f"Environment {env_config['name']} has been updated or created.")

    @catch_exception
    def create_or_update_docker_environment(self, docker_env_config: dict) -> None:
        """
        Creates or updates a Docker environment based on provided configuration.

        Args:
            docker_env_config : The configuration details for Docker environment.
        """
        existing_env = next((env for env in self.ml_client.environments.list() 
                            if env.name == docker_env_config['name']), None)

        if existing_env:
            existing_env = self.ml_client.environments.get(name=existing_env.name, 
                                                        version=existing_env.latest_version)
            if  docker_env_config['version'] <= existing_env.version:
                self.logger.info(f"Environment '{docker_env_config['name']}' with version {docker_env_config['version']} already exists. No changes have been made.")
                return

            self.logger.info(f"Updating the environment {docker_env_config['name']}.")
        else:
            self.logger.info(f"Creating new Docker environment {docker_env_config['name']}.")

        env = Environment(build=BuildContext(path=docker_env_config['BuildContext']['path']), 
                        name=docker_env_config['name'], 
                        version=docker_env_config['version'])

        self.ml_client.environments.create_or_update(env)
        self.logger.info(f"Docker environment {docker_env_config['name']} has been updated or created.")


def main() -> None:
    """Entry point for the script."""
    if len(sys.argv) < 2:
        print('No configuration file provided.')
        sys.exit(1)

    logger = setup_logger(__name__)
    log_event(logger, 'info', f"Reading configuration file: {sys.argv[1]}")
    log_event(logger, 'info', "Initializing ml client...")
    try:
        ml_client = initialize_mlclient()
        env_manager = EnvironmentManager(ml_client, logger)

        with open(sys.argv[1], 'r') as config_file:
            config = json.load(config_file)

        for env_config in config.get('conda', []):
            env_manager.create_or_update_environment(env_config)

        for docker_env_config in config.get('docker_build', []):
            env_manager.create_or_update_docker_environment(docker_env_config)
    except Exception as e:
        log_event(logger, 'error', f"An error occurred during execution: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
