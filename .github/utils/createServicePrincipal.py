# import subprocess
import os
# import json
import os

for key, value in os.environ.items():
    print(f"{key}={value}")


# Replace these values with your own
subscription_ids = os.environ["SUBSCRIPTION_ID"]
sp_names = os.environ["SP_NAME"]

# # Create a new GitHub App
# app_create_command = f"gh auth login"
# subprocess.run(app_create_command, capture_output=True, shell=True)

# # Create a new Azure Service Principal
# az_create_command = f"az ad sp create-for-rbac --name {sp_name} --role Contributor --scopes /subscriptions/{subscription_id} --sdk-auth"
# az_response = subprocess.run(az_create_command, capture_output=True, shell=True)

# # Get the Azure credentials
# az_credentials = az_response.stdout.decode("utf-8")

# # Login to Azure using the service principal
# az_login_command = f"az login --service-principal -u {json.loads(az_credentials)['clientId']} -p {json.loads(az_credentials)['clientSecret']} --tenant {json.loads(az_credentials)['tenantId']}"
# subprocess.run(az_login_command, shell=True)

# # Set the Azure subscription context
# az_set_subscription_command = f"az account set --subscription {subscription_id}"
# subprocess.run(az_set_subscription_command, shell=True)
