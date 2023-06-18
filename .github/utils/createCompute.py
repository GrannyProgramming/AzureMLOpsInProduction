from typing import Tuple, Dict, Union
from azure.ai.ml.entities import AmlCompute, ComputeInstance
from workflowhelperfunc.workflowhelper import setup_logger, log_event, initialize_mlclient, load_config
import os

class ComputeManager:
    """Manage Azure ML Compute resources.
    """

    def __init__(self):
        """Initialize ComputeManager with environment variables, directories, config, and Azure ML client."""
        self.logger = setup_logger(__name__)

        self.environment = self.get_env_variables()

        self.script_dir, self.root_dir = self.get_directory_structure()
        self.config_file = self.get_config()
        self.config = load_config(self.config_file)
        self.client = initialize_mlclient()

        self.compute_types = {
            "amlcompute": AmlCompute,
            "computeinstance": ComputeInstance
        }

    @staticmethod
    def get_env_variables() -> str:
        """Fetch environment variables.

        Returns:
            The environment variable.
        """
        return os.environ['ENVIRONMENT']

    @staticmethod
    def get_directory_structure() -> Tuple[str, str]:
        """Determine current script and root directory.

        Returns:
            A tuple with the script and root directory.
        """
        script_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.join(script_dir, '..', '..')
        return script_dir, root_dir

    def get_config(self) -> str:
        """Identify path for the config.

        Returns:
            The config file path.
        """
        config_file = os.path.join(self.root_dir, "variables", f'{self.environment}', "compute", "compute.json")
        return config_file

    def handle_existing_compute(self, compute_type: str, compute_name: str) -> bool:
        """Check if the compute resource already exists.

        Args:
            compute_type (str): Type of the compute resource.
            compute_name (str): Name of the compute resource.

        Returns:
            True if the compute resource already exists, False otherwise.
        """
        try:
            if self.client.compute.get(compute_name) is not None:
                log_event(self.logger, 'info', f"{compute_type.capitalize()} compute '{compute_name}' already exists.")
                return True
        except Exception as e:
            if 'Not Found' in str(e):
                log_event(self.logger, 'info', f"{compute_type.capitalize()} compute '{compute_name}' does not exist and will be created.")
            else:
                log_event(self.logger, 'error', f"An unexpected error occurred: {e}")
            return False
        return False

    def execute(self):
        """Execute the main logic for managing compute resources."""
        for compute_config in self.config["computes"]:
            compute_type = compute_config.pop("type").lower()
            compute_name = compute_config.pop("name")

            if self.handle_existing_compute(compute_type, compute_name):
                continue

            if compute_type in self.compute_types:
                compute = self.compute_types[compute_type](name=compute_name, **compute_config)
                self.client.compute.begin_create_or_update(compute)
                log_event(self.logger, 'info', f"{compute_type.capitalize()} compute '{compute_name}' has been created.")

if __name__ == "__main__":
    """Main execution of the script: Initialize the ComputeManager and execute it."""
    manager = ComputeManager()
    manager.execute()
