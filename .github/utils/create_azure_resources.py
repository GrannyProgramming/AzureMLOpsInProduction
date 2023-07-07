import os
import json
import subprocess
import argparse
from pathlib import Path
from workflowhelperfunc.workflowhelper import setup_logger, log_event


class BicepDeployment:
    """
    A class to handle the deployment process using Bicep templates.
    """

    def __init__(self, logger, template_file: str, parameters: str) -> None:
        """
        Initialize the BicepDeployment class with a logger, template file, and parameters.

        Args:
            logger: The logger instance for logging events.
            template_file: The Bicep template file.
            parameters: The parameters for the Bicep file.
        """
        self.template_file = template_file
        self.parameters = parameters
        self.logger = logger

    @classmethod
    def get_env_variable(cls, instance, var_name: str) -> str:
        """
        Retrieve the value of the specified environment variable.

        Args:
            var_name: The name of the environment variable.

        Raises:
            Exception: If the specified environment variable is not set.

        Returns:
            The value of the specified environment variable.
        """
        try:
            return os.environ[var_name]
        except KeyError:
            log_event(instance.logger, 'error', f'{var_name} environment variable not set')
            raise


    def get_location_from_parameters_file(self, parameters_file: str) -> str:
        """
        Retrieve the location value from the specified parameters JSON file.

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
            raise FileNotFoundError(f'Parameters file {parameters_file} does not exist')

        with parameters_file_path.open('r') as f:
            parameters = json.load(f)

        try:
            return parameters['parameters']['location']['value']
        except KeyError:
            log_event(self.logger, 'error', 'Location is not specified in the parameters file')
            raise

    def run_command(self, cmd: str) -> str:
        """
        Run a shell command and returns its output. Raises an exception if it fails.

        Args:
            cmd: The shell command.

        Raises:
            Exception: If the command fails.

        Returns:
            The output from the shell command.
        """
        log_event(self.logger, 'info', f'Running command: {cmd}')
        process = subprocess.run(cmd, shell=True, capture_output=True)

        if process.returncode != 0:
            log_event(self.logger, 'error', f'Command failed with error:\n{process.stderr.decode()}')
            raise Exception(f'Command failed with error:\n{process.stderr.decode()}')

        return process.stdout.decode()

    def create_bicep_deployment(self, location: str) -> str:
        """
        Create a Bicep deployment using the Azure CLI.

        Args:
            location: The location for the Bicep deployment.

        Returns:
            The output from the Azure CLI command.
        """
        cmd = f'az deployment sub create --location {location} --template-file {self.template_file} --parameters {self.parameters}'
        return self.run_command(cmd)

    def set_aml_workspace_and_resource_group_as_defaults(self, workspace: str, resource_group: str) -> None:
        """
        Set the AML workspace and its resource group as defaults using the Azure CLI.

        Args:
            workspace: The AML workspace.
            resource_group: The resource group of the AML workspace.
        """
        log_event(self.logger, 'info', f'Setting {workspace} as default workspace and {resource_group} as default resource group')
        self.run_command(f'az configure --defaults group={resource_group}')
        self.run_command(f'az configure --defaults workspace={workspace}')

    def execute(self) -> None:
        """
        The main function for executing the Bicep deployment process.
        """
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


def main() -> None:
    logger = setup_logger(__name__)

    parser = argparse.ArgumentParser(description='Create a Bicep deployment.')

    deploy = BicepDeployment(logger, None, None)  # create instance with None parameters temporarily

    parser.add_argument('--template-file', default=deploy.get_env_variable(deploy, 'BICEP_MAIN_PATH'),
                        help='Bicep template file')
    parser.add_argument('--parameters', default=deploy.get_env_variable(deploy, 'BICEP_PARAMETER_PATH'),
                        help='Parameters for the Bicep file')

    args = parser.parse_args()

    # Assign the correct parameters after parsing the command line arguments
    deploy.template_file = args.template_file
    deploy.parameters = args.parameters
    deploy.execute()


if __name__ == '__main__':
    main()
