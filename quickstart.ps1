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
$sp = az ad sp create-for-rbac --name $SP_NAME --role Owner --scopes /subscriptions/$SUBSCRIPTION_ID | ConvertFrom-Json

# Save the service principal credentials to GitHub Secrets
$clientId = $sp.appId
$clientSecret = $sp.password
$tenantId = $sp.tenant

gh auth login 

# Set the GitHub secrets using GitHub CLI
gh secret set ARM_CLIENT_ID -r "$GH_OWNER/$GH_REPO" --body "$clientId"
gh secret set ARM_CLIENT_SECRET -r "$GH_OWNER/$GH_REPO" --body "$clientSecret"
gh secret set ARM_TENANT_ID -r "$GH_OWNER/$GH_REPO" --body "$tenantId"

echo "Service principal created and saved in GitHub Secrets"
echo $sp