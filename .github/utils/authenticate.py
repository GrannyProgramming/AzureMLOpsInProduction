import argparse
import subprocess

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('environment', choices=['dev', 'test', 'prod'])
    args = parser.parse_args()

    # Get the service principal credentials from GitHub secrets
    subscription_id = subprocess.check_output(['bash', '-c', 'echo $AZURE_SUBSCRIPTION_ID']).decode().strip()
    tenant_id = subprocess.check_output(['bash', '-c', 'echo $AZURE_TENANT_ID']).decode().strip()
    client_id = subprocess.check_output(['bash', '-c', 'echo $AZURE_CLIENT_ID']).decode().strip()
    client_secret = subprocess.check_output(['bash', '-c', 'echo $AZURE_CLIENT_SECRET']).decode().strip()

    # Use the Azure CLI to authenticate with the service principal
    subprocess.run([
        'az', 'login', '--service-principal',
        '--username', client_id,
        '--password', client_secret,
        '--tenant', tenant_id,
    ])

    # Set the default subscription based on the environment
    if args.environment == 'dev':
        subscription_name = 'Development'
    elif args.environment == 'test':
        subscription_name = 'Testing'
    elif args.environment == 'prod':
        subscription_name = 'Production'

    subprocess.run(['az', 'account', 'set', '--subscription', subscription_name])

if __name__ == '__main__':
    main()
