import subprocess
import os
import json

# Replace these values with your own
subscription_id = os.environ["AZURE_SUBSCRIPTION_ID"]
sp_name = os.environ["AZURE_SP_NAME"]

# Create a new GitHub App
app_create_command = f"gh auth login"
subprocess.run(app_create_command, capture_output=True, shell=True)

app_create_command = f"gh api /authorizations -X POST -H 'Accept: application/vnd.github.v3+json' -d '{{\"scopes\": [\"admin:org\", \"repo\"], \"note\": \"My authorization\"}}'"
app_response = subprocess.run(app_create_command, capture_output=True, shell=True)

# Get the GitHub token
gh_token = app_response.stdout.decode("utf-8")
gh_token = gh_token.split(": ")[1].strip()

# Create a new Azure Service Principal
az_create_command = f"az ad sp create-for-rbac --name {sp_name} --role Contributor --scopes /subscriptions/{subscription_id} --sdk-auth"
az_response = subprocess.run(az_create_command, capture_output=True, shell=True)

# Get the Azure credentials
az_credentials = az_response.stdout.decode("utf-8")

# Login to Azure using the service principal
az_login_command = f"az login --service-principal -u {json.loads(az_credentials)['clientId']} -p {json.loads(az_credentials)['clientSecret']} --tenant {json.loads(az_credentials)['tenantId']}"
subprocess.run(az_login_command, shell=True)

# Set the Azure subscription context
az_set_subscription_command = f"az account set --subscription {subscription_id}"
subprocess.run(az_set_subscription_command, shell=True)

# Set the GitHub App token as an environment variable
set_gh_token_command = f"export GH_TOKEN={gh_token}"
subprocess.run(set_gh_token_command, shell=True)

# Authenticate with the GitHub App
gh_auth_command = f"gh auth login --with-token <<< '${{ GH_TOKEN }}'"
subprocess.run(gh_auth_command, shell=True)
