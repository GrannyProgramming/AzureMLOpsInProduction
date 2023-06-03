import os
import subprocess
from workflowhelperfunc.workflowhelper import setup_logger, log_event

def login_to_service_principal(logger):
    """
    Login to the Azure service principal.
    
    This function logs in to the Azure service principal using the az cli. 
    It gets the credentials from the environment variables ARM_CLIENT_ID, ARM_CLIENT_SECRET, and ARM_TENANT_ID.
    
    Parameters:
    logger (Logger): Logger object for logging events.

    Raises:
    Exception: If any of the required environment variables are missing.
    """
    # Get secrets from environment variables
    arm_client_id = os.getenv('ARM_CLIENT_ID')
    arm_client_secret = os.getenv('ARM_CLIENT_SECRET')
    arm_tenant_id = os.getenv('ARM_TENANT_ID')

    if not all([arm_client_id, arm_client_secret, arm_tenant_id]):
        log_event(logger, 'error', "One or more required environment variables are missing!")
        raise Exception("One or more required environment variables are missing!")

    # Use az cli to log in
    login_command = [
        'az', 'login',
        '--service-principal',
        '--username', arm_client_id,
        '--password', arm_client_secret,
        '--tenant', arm_tenant_id
    ]

    try:
        # Call the login command
        subprocess.check_call(login_command)
        log_event(logger, 'info', "Successfully logged into the Azure service principal.")
    except subprocess.CalledProcessError as e:
        log_event(logger, 'error', f"Failed to login: {e}")
        raise

if __name__ == '__main__':
    """
    Main execution of the script: Setup the logger and login to the Azure service principal.
    """
    logger = setup_logger(__name__)    
    # Call the function
    try:
        login_to_service_principal(logger)
    finally:
        for handler in logger.handlers:  # Close handlers to flush all logs
            handler.close()
            logger.removeHandler(handler)

