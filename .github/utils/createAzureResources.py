import os
import json
import subprocess
import argparse
import logging
from pathlib import Path
from workflowhelperfunc.workflowhelper import load_and_set_env_vars

class BicepDeployment:
    """A class for creating a Bicep deployment."""

    def __init__(self, template_file, parameters):
        """Initialize with the Bicep template file and parameters."""
        self.template_file = template_file
        self.parameters = parameters

    @staticmethod
    def get_env_variable(var_name):
        """Get environment variable or raise exception if it's not present."""
        if var_name in os.environ:
            return os.environ[var_name]
        else:
            raise Exception(f"{var_name} environment variable not set")

    @staticmethod
    def get_location_from_parameters_file(parameters_file):
        """Extract the location value from the parameters JSON file."""
        parameters_file_path = Path(parameters_file)
        if not parameters_file_path.is_file():
            raise Exception(f'Parameters file {parameters_file} does not exist')

        with parameters_file_path.open('r') as f:
            parameters = json.load(f)

        if 'parameters' in parameters and 'location' in parameters['parameters'] and 'value' in parameters['parameters']['location']:
            return parameters['parameters']['location']['value']
        else:
            raise Exception('Location is not specified in the parameters file')

    @staticmethod
    def run_command(cmd):
        """Run shell command and return its output. Raise exception if it fails."""
        with subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as process:
            stdout, stderr = process.communicate()

        if process.returncode != 0:
            raise Exception(f'Command failed with error:\n{stderr.decode()}')
        else:
            return stdout.decode()

    def create_bicep_deployment(self, location):
        """Create a Bicep deployment using the Azure CLI."""
        cmd = f'az deployment sub create --location {location} --template-file {self.template_file} --parameters {self.parameters}'
        return self.run_command(cmd)

    @staticmethod
    def set_aml_workspace_and_resource_group_as_defaults(workspace, resource_group):
        """Set the AML workspace and its resource group as defaults using the Azure CLI."""
        BicepDeployment.run_command(f'az configure --defaults group={resource_group}')
        BicepDeployment.run_command(f'az configure --defaults workspace={workspace}')

    def execute(self):
        """Main function."""
        try:
            location = self.get_location_from_parameters_file(self.parameters)
            output = self.create_bicep_deployment(location)

            # Parse workspace and resource group from output
            output_json = json.loads(output)
            workspace = output_json['properties']['outputs']['workspaceName']['value']
            resource_group = output_json['properties']['outputs']['resourceGroupName']['value']

            # Set these vars in gh environment
            load_and_set_env_vars(None, [f'workspace_name={workspace}', f'resource_group={resource_group}'])

            # Set workspace and resource group as defaults
            self.set_aml_workspace_and_resource_group_as_defaults(workspace, resource_group)

            # Check if workspace and resource group are set as defaults
            default_settings = json.loads(self.run_command('az configure --list-defaults -o json'))
            default_workspace = next((x for x in default_settings if x['name'] == 'workspace'), None)
            default_resource_group = next((x for x in default_settings if x['name'] == 'group'), None)

            if default_workspace and default_workspace['value'] == workspace:
                logging.info(f"Default workspace is set to: {workspace}")
            else:
                logging.error("Default workspace is not set correctly")

            if default_resource_group and default_resource_group['value'] == resource_group:
                logging.info(f"Default resource group is set to: {resource_group}")
            else:
                logging.error("Default resource group is not set correctly")

            logging.info(f'Command succeeded with output:\n{output}')
        except Exception as e:
            logging.error(f'Failed to create Bicep deployment: {e}')


if __name__ == '__main__':
    """Main execution of the script: Initialize the BicepDeployment and execute it."""
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(description='Create a Bicep deployment.')
    parser.add_argument('--template-file', default=BicepDeployment.get_env_variable('BICEP_MAIN_PATH'),
                        help='Bicep template file')
    parser.add_argument('--parameters', default=BicepDeployment.get_env_variable('BICEP_PARAMETER_PATH'),
                        help='Parameters for the Bicep file')

    args = parser.parse_args()

    deploy = BicepDeployment(args.template_file, args.parameters)
    deploy.execute()
