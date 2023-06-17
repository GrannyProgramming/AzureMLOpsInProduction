import json
import sys
from azure.ai.ml.entities import Environment, BuildContext
import ruamel.yaml as yaml
from workflowhelperfunc.workflowhelper import initialize_mlclient, setup_logger, log_event

class EnvironmentManager:
    """
    Class to manage Azure ML environments.

    Attributes:
        ml_client: Azure ML client to handle Azure ML related operations.
        logger: Logger to log the operations.
    """
    def __init__(self, ml_client: object, logger: object) -> None:
        """
        Initialize the manager with an Azure ML client and a logger.

        Args:
            ml_client (object): Azure ML client object.
            logger (object): Logger object.
        """
        self.ml_client = ml_client
        self.logger = logger

    def create_yaml_file(self, filename: str, content: dict) -> None:
        """
        Create a YAML file from content.

        Args:
            filename (str): Name of the file to be created.
            content (dict): Content to be written to the file.
        """
        try:
            with open(filename, 'w') as file:
                yaml_handler = yaml.YAML()
                yaml_handler.indent(mapping=2, sequence=4, offset=2)
                yaml_handler.dump(content, file)
        except Exception as e:
            self.logger.error(f"Failed to create YAML file: {filename}. Error: {e}")
            raise

    def prepare_env_config(self, config: dict, new_version: str) -> dict:
        """
        Prepare environment configuration.

        Args:
            config (dict): The configuration details.
            new_version (str): The new version of the environment.

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

    def create_or_update_environment(self, env_config: dict) -> None:
        """
        Create or update environment based on provided configuration.

        Args:
            env_config (dict): The configuration details.
        """
        try:
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
                else:
                    if env_config['version'] == "auto":
                        new_version = str(int(existing_env.version) + 1)  # auto increment
                    else:
                        new_version = env_config['version']

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
        except Exception as e:
            self.logger.error(f"Failed to create or update environment: {env_config['name']}. Error: {e}")
            raise

    def create_or_update_docker_environment(self, docker_env_config: dict) -> None:
        """
        Create or update Docker environment based on provided configuration.

        Args:
            docker_env_config (dict): The configuration details for Docker environment.
        """
        try:
            existing_env = next((env for env in self.ml_client.environments.list() 
                                if env.name == docker_env_config['name']), None)

            if existing_env:
                existing_env = self.ml_client.environments.get(name=existing_env.name, 
                                                            version=existing_env.latest_version)
                if  docker_env_config['version'] <= existing_env.version:
                    self.logger.info(f"Environment '{docker_env_config['name']}' with version {docker_env_config['version']} already exists. No changes have been made.")
                    return
                else:
                    self.logger.info(f"Updating the environment {docker_env_config['name']}.")
            else:
                self.logger.info(f"Creating new Docker environment {docker_env_config['name']}.")

            env = Environment(build=BuildContext(path=docker_env_config['BuildContext']['path']), 
                            name=docker_env_config['name'], 
                            version=docker_env_config['version'])
                            
            self.ml_client.environments.create_or_update(env)
            self.logger.info(f"Docker environment {docker_env_config['name']} has been updated or created.")
        except Exception as e:
            self.logger.error(f"Failed to create or update Docker environment: {docker_env_config['name']}. Error: {e}")
            raise


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

        for env_config in config['conda']:
            env_manager.create_or_update_environment(env_config)
        
        if 'docker_build' in config:
            for docker_env_config in config['docker_build']:
                env_manager.create_or_update_docker_environment(docker_env_config)


    except Exception as e:
        log_event(logger, 'error', f"An error occurred during execution: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
