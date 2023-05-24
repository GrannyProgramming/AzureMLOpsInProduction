'''
Azure CLI (az): The Azure CLI is a command-line tool that you can use to manage Azure resources. It is used in this script to login to your Azure account, set your subscription, and create a service principal. You can install it by following the instructions on this page: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli

GitHub CLI (gh): GitHub CLI brings GitHub to your terminal. It reduces context switching, helps you focus, and enables you to more easily script and create automation. It is used in this script to set GitHub secrets. You can install it by following the instructions on this page: https://cli.github.com/manual/installation 

Restart terminal after installing all the above
'''

# Define the variables
$PARAMS_FILE = $args[0]  # Accept the JSON file as the first command-line argument

# Check if the parameters file is provided
if (!$PARAMS_FILE -or !(Test-Path $PARAMS_FILE)) {
    Write-Error "Please provide a valid JSON file as the first command-line argument"
    Exit 1
}

# Load the JSON content
$jsonContent = Get-Content -Path $PARAMS_FILE | ConvertFrom-Json

# Authenticate with GitHub
gh auth login

# Initialize service principal name and credentials
$previousSPName = $null
$clientId = $null
$clientSecret = $null
$tenantId = $null

# Iterate through each environment from the JSON file
foreach ($env in $jsonContent.PSObject.Properties.Name) {
    $envDetails = $jsonContent.$env

    # Extract the variables from the JSON content
    $SUBSCRIPTION_ID = $envDetails.subscription_id
    $SP_NAME = $envDetails.sp_name
    $GH_URL = $envDetails.gh_address

    # Remove the 'https://github.com/' part
    $GH_OWNER, $GH_REPO = ($GH_URL -replace 'https://github.com/', '') -split '/', 2

    # Login to Azure
    az login

    # Set the subscription ID
    az account set --subscription $SUBSCRIPTION_ID

    # Create the service principal and extract the credentials if the SP name is different from the previous one
    if ($SP_NAME -ne $previousSPName) {
        $sp = az ad sp create-for-rbac --name $SP_NAME --role Owner --scopes /subscriptions/$SUBSCRIPTION_ID | ConvertFrom-Json
        $clientId = $sp.appId
        $clientSecret = $sp.password
        $tenantId = $sp.tenant

        # Update the previous SP name
        $previousSPName = $SP_NAME
    }

    # Create the environment
    gh api repos/$GH_OWNER/$GH_REPO/environments -X POST -F name=$env

    gh secret set ARM_CLIENT_ID -r "$GH_OWNER/$GH_REPO" --body $clientId --env=$env
    gh secret set ARM_CLIENT_SECRET -r "$GH_OWNER/$GH_REPO" --body $clientSecret --env=$env
    gh secret set ARM_TENANT_ID -r "$GH_OWNER/$GH_REPO" --body $tenantId --env=$env
}

echo "Service principals created and saved in GitHub Secrets"
