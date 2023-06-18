import os
import subprocess
import logging


def get_env_variable(name):
    """
    Get the environment variable or return exception.

    This function tries to get the value of an environment variable.
    If the environment variable is not set, it logs an error message and raises an exception.

    Parameters:
    name (str): The name of the environment variable.

    Returns:
    str: The value of the environment variable.

    Raises:
    Exception: If the environment variable is not set.
    """
    try:
        return os.environ[name]
    except KeyError:
        logging.error(f"Environment variable {name} not set.")
        raise


def login_to_service_principal(client_id, client_secret, tenant_id):
    """
    Login to the Azure service principal.
    
    This function logs in to the Azure service principal using the az cli. 
    It gets the credentials from the provided arguments.

    Parameters:
    client_id (str): The client id of the Azure service principal.
    client_secret (str): The client secret of the Azure service principal.
    tenant_id (str): The tenant id of the Azure service principal.

    Raises:
    subprocess.CalledProcessError: If the az cli login command fails.
    """
    login_command = [
        'az', 'login',
        '--service-principal',
        '--username', client_id,
        '--password', client_secret,
        '--tenant', tenant_id
    ]

    try:
        subprocess.check_call(login_command)
        logging.info("Successfully logged into the Azure service principal.")
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to login: {e}")
        raise


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    
    client_id = get_env_variable('ARM_CLIENT_ID')
    client_secret = get_env_variable('ARM_CLIENT_SECRET')
    tenant_id = get_env_variable('ARM_TENANT_ID')

    login_to_service_principal(client_id, client_secret, tenant_id)
