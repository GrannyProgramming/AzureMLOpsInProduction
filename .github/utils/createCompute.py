from azure.identity import DefaultAzureCredential
from azure.ai.ml import MLClient
from azure.ai.ml.entities import AmlCompute, ComputeInstance
from workflowhelperfunc.workflowhelper import setup_logger, log_event
import os
import json 

class ComputeManager:
    """Manage Azure ML Compute resources."""
    def __init__(self):
        """Initialize ComputeManager with environment variables, directories, config, and Azure ML client."""
        self.logger = setup_logger(__name__)

        self.environment, self.subscription_id, self.workspace_name, self.resource_group = self.get_env_variables()
        self.script_dir, self.root_dir = self.get_directory_structure()
        self.config_file = self.get_config()
        self.config = self.load_config(self.config_file)
        
        self.credential = DefaultAzureCredential()
        self.client = MLClient(credential=self.credential, subscription_id=f'{self.subscription_id}', workspace_name=f'{self.workspace_name}', resource_group_name=f'{self.resource_group}')

        self.compute_types = {
            "amlcompute": AmlCompute,
            "computeinstance": ComputeInstance
        }

    @staticmethod
    def get_env_variables():
        """Fetch environment variables.

        Returns:
            tuple: environment, subscription_id, workspace_name, resource_group
        """
        return os.environ['ENVIRONMENT'], os.environ['SUBSCRIPTION_ID'], os.environ['WORKSPACE_NAME'], os.environ['RESOURCE_GROUP']

    @staticmethod
    def get_directory_structure():
        """Determine current script and root directory.

        Returns:
            tuple: script_dir, root_dir
        """
        script_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.join(script_dir, '..', '..')
        return script_dir, root_dir

    def get_config(self):
        """Identify path for the config.

        Returns:
            str: config_file
        """
        config_file = os.path.join(self.root_dir, "variables", f'{self.environment}', "compute", "compute.json")
        return config_file

    @staticmethod
    def load_config(config_file):
        """Load the configuration from a JSON file.

        Args:
            config_file (str): JSON file to load the configuration from.

        Returns:
            dict: Loaded configuration.
        """
        with open(config_file, "r") as f:
            return json.load(f)

    def handle_existing_compute(self, compute_type, compute_name):
        """Check if the compute resource already exists. If so, return True.

        Args:
            compute_type (str): Type of the compute resource.
            compute_name (str): Name of the compute resource.

        Returns:
            bool: True if the compute resource already exists, False otherwise.
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
