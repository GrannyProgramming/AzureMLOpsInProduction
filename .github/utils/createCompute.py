from azure.identity import DefaultAzureCredential
from azure.ai.ml import MLClient, load_compute
from azure.ai.ml.entities import AmlCompute, ComputeInstance
import os
import json 

class ComputeManager:
    def __init__(self):
        """Initialize ComputeManager by setting up variables and Azure ML client."""
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
        """Fetch and return the environment variables."""
        return os.environ['ENVIRONMENT'], os.environ['SUBSCRIPTION_ID'], os.environ['WORKSPACE_NAME'], os.environ['RESOURCE_GROUP']

    @staticmethod
    def get_directory_structure():
        """Determine and return the current script directory and root directory."""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.join(script_dir, '..', '..')
        return script_dir, root_dir

    def get_config(self):
        """Identify and return the paths for the config"""
        config_file = os.path.join(self.root_dir, "variables", f'{self.environment}', "compute", "compute.json")
        return config_file

    @staticmethod
    def load_config(config_file):
        """Load the configuration from a JSON file."""
        with open(config_file, "r") as f:
            return json.load(f)

    def handle_existing_compute(self, compute_type, compute_name):
        """Check if the compute resource already exists. If so, return True."""
        try:
            if self.client.compute.get(compute_name) is not None:
                print(f"{compute_type.capitalize()} compute '{compute_name}' already exists.")
                return True
        except Exception as e:
            print(f"Error occurred: {e}")
            return False
        return False

    def execute(self):
        """Execute the main logic: """
        for compute_config in self.config["computes"]:
            compute_type = compute_config.pop("type").lower()
            compute_name = compute_config.pop("name")

            if self.handle_existing_compute(compute_type, compute_name):
                continue

            if compute_type in self.compute_types:
                compute = self.compute_types[compute_type](name=compute_name, **compute_config)
                self.client.compute.begin_create_or_update(compute)
                print(f"{compute_type.capitalize()} compute '{compute_name}' has been created.")

if __name__ == "__main__":
    """Main execution of the script: Initialize the ComputeManager and execute it."""
    manager = ComputeManager()
    manager.execute()
