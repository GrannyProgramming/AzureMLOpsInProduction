import os
import subprocess

def login_to_service_principal():
    # Get secrets from environment variables
    arm_client_id = os.getenv('ARM_CLIENT_ID')
    arm_client_secret = os.getenv('ARM_CLIENT_SECRET')
    arm_tenant_id = os.getenv('ARM_TENANT_ID')

    if not all([arm_client_id, arm_client_secret, arm_tenant_id]):
        raise Exception("One or more required environment variables are missing!")

    # Use az cli to log in
    login_command = [
        'az', 'login',
        '--service-principal',
        '--username', arm_client_id,
        '--password', arm_client_secret,
        '--tenant', arm_tenant_id
    ]

    # Call the login command
    subprocess.check_call(login_command)

# Call the function
login_to_service_principal()
