import subprocess
import json
import requests
import os

# Define the required GitHub API parameters
github_url = os.environ["GH_ADDRESS"]

# Define the required GitHub CLI command to create a token
gh_cli_command = 'gh auth login --with-token --silent --json'

# Execute the GitHub CLI command and capture the output
output1 = subprocess.check_output(gh_cli_command.split()).decode('utf-8')

# Parse the output to retrieve the token
token = json.loads(output1)['token']

az_cli_command = f'az ad sp create-for-rbac -n {os.environ["SP_NAME"]} --sdk-auth'

# Execute the Azure CLI command and capture the output
output = subprocess.check_output(az_cli_command.split()).decode('utf-8')

# Parse the output to retrieve the necessary information
credentials = json.loads(output)
client_id = credentials['clientId']
client_secret = credentials['clientSecret']
tenant_id = credentials['tenantId']
subscription_id = credentials['subscriptionId']

secrets = {
    'AZURE_CLIENT_ID': client_id,
    'AZURE_CLIENT_SECRET': client_secret,
    'AZURE_TENANT_ID': tenant_id,
    'AZURE_SUBSCRIPTION_ID': subscription_id
}

# Loop through the secrets and create/update them on GitHub
for name, value in secrets.items():
    secret_url = github_url + '/' + name
    data = {'encrypted_value': value.encode('utf-8').hex()}
    headers = {'Authorization': f'token {token}'}
    response = requests.put(secret_url, headers=headers, json=data)

    if response.status_code == 204:
        print(f'Successfully created/updated secret: {name}')
    else:
        print(f'Failed to create/update secret: {name}')
