'''
Azure CLI (az): The Azure CLI is a command-line tool that you can use to manage Azure resources. It is used in this script to login to your Azure account, set your subscription, and create a service principal. You can install it by following the instructions on this page: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli

GitHub CLI (gh): GitHub CLI brings GitHub to your terminal. It reduces context switching, helps you focus, and enables you to more easily script and create automation. It is used in this script to set GitHub secrets. You can install it by following the instructions on this page: https://cli.github.com/manual/installation 

jq: jq is a lightweight and flexible command-line JSON processor. It is like sed for JSON data. It is used in this script to parse the JSON output of the Azure CLI command. You can install it by following the instructions on this page: https://stedolan.github.io/jq/download/

Restart terminal after installing all the above
'''
# Define the variables
$PARAMS_FILE = $args[0]  # Accept the JSON file as the first command-line argument

# Check if the parameters file is provided
if ($PARAMS_FILE) {
    # Load the JSON content
    $jsonContent = Get-Content -Path $PARAMS_FILE | ConvertFrom-Json

    # Extract the variables from the JSON content
    $SUBSCRIPTION_ID = $jsonContent.subscription_id
    $SP_NAME = $jsonContent.sp_name
    $GH_URL = $jsonContent.gh_address
} else {
    # If the parameters file is not provided, prompt for user input
    $SUBSCRIPTION_ID = Read-Host -Prompt "Enter Your Azure Subscription ID"
    $SP_NAME = Read-Host -Prompt "Enter Your Service Principal Name"
    $GH_URL = Read-Host -Prompt "Enter Your GitHub URL"
}

# Remove the 'https://github.com/' part
$GH_URL = $GH_URL -replace 'https://github.com/', ''

# Extract GH_OWNER and GH_REPO
$GH_OWNER, $GH_REPO = $GH_URL -split '/', 2

# Login to Azure
az login

# Set the subscription ID
az account set --subscription $SUBSCRIPTION_ID

# Create the service principal
$sp = az ad sp create-for-rbac --name $SP_NAME --sdk-auth

# Save the service principal credentials to GitHub Secrets
# NOTE: You need to have 'jq' utility installed in your system or use an equivalent in PowerShell to parse the JSON output
$clientId = $(echo $sp | jq -r '.clientId')
$clientSecret = $(echo $sp | jq -r '.clientSecret')
$tenantId = $(echo $sp | jq -r '.tenantId')

gh auth login 
# Set the GitHub secrets using GitHub CLI
echo $clientId | gh secret set AZURE_CLIENT_ID -r "$GH_OWNER/$GH_REPO" --body "$clientId"
echo $clientSecret | gh secret set AZURE_CLIENT_SECRET -r "$GH_OWNER/$GH_REPO" --body "$clientSecret"
echo $tenantId | gh secret set AZURE_TENANT_ID -r "$GH_OWNER/$GH_REPO" --body "$tenantId"
echo $sp | gh secret set AZURE_CREDENTIALS -r "$GH_OWNER/$GH_REPO" --body "$sp"

echo "Service principal created and saved in GitHub Secrets"
