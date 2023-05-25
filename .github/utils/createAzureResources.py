import os
import json
import subprocess
import argparse
import logging
from pathlib import Path

def get_env_variable(var_name):
    """Get environment variable or raise exception if it's not present."""
    if var_name in os.environ:
        return os.environ[var_name]
    else:
        raise Exception(f"{var_name} environment variable not set")

def get_location_from_parameters_file(parameters_file):
    """Extract the location value from the parameters JSON file."""
    parameters_file_path = Path(parameters_file)
    if not parameters_file_path.is_file():
        raise Exception(f'Parameters file {parameters_file} does not exist')

    with parameters_file_path.open('r') as f:
        parameters = json.load(f)

    if 'location' in parameters and 'value' in parameters['location']:
        return parameters['location']['value']
    else:
        raise Exception('Location is not specified in the parameters file')

def run_command(cmd):
    """Run shell command and return its output. Raise exception if it fails."""
    with subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as process:
        stdout, stderr = process.communicate()

    if process.returncode != 0:
        raise Exception(f'Command failed with error:\n{stderr.decode()}')
    else:
        return stdout.decode()

def create_bicep_deployment(location, template_file, parameters):
    """Create a Bicep deployment using the Azure CLI."""
    cmd = f'az deployment sub create --location {location} --template-file {template_file} --parameters {parameters}'
    return run_command(cmd)

def main():
    """Main function."""
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(description='Create a Bicep deployment.')
    parser.add_argument('--template-file', default=get_env_variable('BICEP_MAIN_PATH'), help='Bicep template file')
    parser.add_argument('--parameters', default=get_env_variable('BICEP_PARAMETER_PATH'), help='Parameters for the Bicep file')

    args = parser.parse_args()

    try:
        location = get_location_from_parameters_file(args.parameters)
        output = create_bicep_deployment(location, args.template_file, args.parameters)
        logging.info(f'Command succeeded with output:\n{output}')
    except Exception as e:
        logging.error(f'Failed to create Bicep deployment: {e}')

if __name__ == '__main__':
    main()
