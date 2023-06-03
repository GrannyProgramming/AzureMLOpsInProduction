import os
import json
import subprocess
import argparse
from pathlib import Path
from workflowhelperfunc.workflowhelper import setup_logger, log_event

class BicepDeployment:
    """A class to handle the deployment process using Bicep templates."""

    def __init__(self, logger, template_file, parameters):
        """Initializes the BicepDeployment class with a logger, template file, and parameters.

        Args:
            logger: The logger instance for logging events.
            template_file: The Bicep template file.
            parameters: The parameters for the Bicep file.
        """
        self.template_file = template_file
        self.parameters = parameters
        self.logger = logger

    @staticmethod
    def get_env_variable(var_name):
        """Retrieves the value of the specified environment variable.

        Args:
            var_name: The name of the environment variable.

        Raises:
            Exception: If the specified environment variable is not set.

        Returns:
            The value of the specified environment variable.
        """
        if var_name in os.environ:
            return os.environ[var_name]
        else:
            raise Exception(f"{var_name} environment variable not set")

    def get_location_from_parameters_file(self, parameters_file):
        """Retrieves the location value from the specified parameters JSON file.

        Args:
            parameters_file: The parameters JSON file.

        Raises:
            Exception: If the parameters file does not exist or the location is not specified.

        Returns:
            The location value from the parameters JSON file.
        """
        parameters_file_path = Path(parameters_file)
        if not parameters_file_path.is_file():
            log_event(self.logger, 'error', f'Parameters file {parameters_file} does not exist')
            raise Exception(f'Parameters file {parameters_file} does not exist')

        with parameters_file_path.open('r') as f:
            parameters = json.load(f)

        if 'parameters' in parameters and 'location' in parameters['parameters'] and 'value' in parameters['parameters']['location']:
            return parameters['parameters']['location']['value']
        else:
            log_event(self.logger, 'error', 'Location is not specified in the parameters file')
            raise Exception('Location is not specified in the parameters file')

    def run_command(self, cmd):
        """Runs a shell command and returns its output. Raises an exception if it fails.

        Args:
            cmd: The shell command.

        Raises:
            Exception: If the command fails.

        Returns:
            The output from the shell command.
        """
        log_event(self.logger, 'info', f'Running command: {cmd}')
        with subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as process:
            stdout, stderr = process.communicate()

        if process.returncode != 0:
            log_event(self.logger, 'error', f'Command failed with error:\n{stderr.decode()}')
            raise Exception(f'Command failed with error:\n{stderr.decode()}')
        else:
            return stdout.decode()

    def create_bicep_deployment(self, location):
        """Creates a Bicep deployment using the Azure CLI.

        Args:
            location: The location for the Bicep deployment.

        Returns:
            The output from the Azure CLI command.
        """
        cmd = f'az deployment sub create --location {location} --template-file {self.template_file} --parameters {self.parameters}'
        return self.run_command(cmd)

    def set_aml_workspace_and_resource_group_as_defaults(logger, workspace, resource_group):
        """Sets the AML workspace and its resource group as defaults using the Azure CLI.

        Args:
            logger: The logger instance for logging events.
            workspace: The AML workspace.
            resource_group: The resource group of the AML workspace.
        """
        log_event(logger, 'info', f'Setting {workspace} as default workspace and {resource_group} as default resource group')
        BicepDeployment.run_command(f'az configure --defaults group={resource_group}')
        BicepDeployment.run_command(f'az configure --defaults workspace={workspace}')

    def execute(self):
        """The main function for executing the Bicep deployment process."""
        try:
            location = self.get_location_from_parameters_file(self.parameters)
            output = self.create_bicep_deployment(location)

            # Parse workspace and resource group from output
            output_json = json.loads(output)
            workspace = output_json['properties']['outputs']['workspaceName']['value']
            resource_group = output_json['properties']['outputs']['resourceGroupName']['value']

            # Set workspace and resource group as defaults
            self.set_aml_workspace_and_resource_group_as_defaults(workspace, resource_group)


            # Check if workspace and resource group are set as defaults
            default_settings = json.loads(self.run_command('az configure --list-defaults -o json'))
            default_workspace = next((x for x in default_settings if x['name'] == 'workspace'), None)
            default_resource_group = next((x for x in default_settings if x['name'] == 'group'), None)

            if default_workspace and default_workspace['value'] == workspace:
                log_event(self.logger, 'info', f"Default workspace is set to: {workspace}")
            else:
                log_event(self.logger, 'error', "Default workspace is not set correctly")

            if default_resource_group and default_resource_group['value'] == resource_group:
                log_event(self.logger, 'info', f"Default resource group is set to: {resource_group}")
            else:
                log_event(self.logger, 'error', "Default resource group is not set correctly")

            log_event(self.logger, 'info', f'Command succeeded with output:\n{output}')
        except Exception as e:
            log_event(self.logger, 'error', f'Failed to create Bicep deployment: {e}')

if __name__ == '__main__':
    """The main entry point of the script. Initializes the BicepDeployment instance and executes it."""
    logger = setup_logger(__name__)

    parser = argparse.ArgumentParser(description='Create a Bicep deployment.')
    parser.add_argument('--template-file', default=BicepDeployment.get_env_variable('BICEP_MAIN_PATH'),
                        help='Bicep template file')
    parser.add_argument('--parameters', default=BicepDeployment.get_env_variable('BICEP_PARAMETER_PATH'),
                        help='Parameters for the Bicep file')

    args = parser.parse_args()

    deploy = BicepDeployment(logger, args.template_file, args.parameters)
    deploy.execute()
