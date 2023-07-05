$PARAMS_FILE = $args[0]  # Accept the JSON file as the first command-line argument

if (!$PARAMS_FILE -or !(Test-Path $PARAMS_FILE)) {
    Write-Error "Please provide a valid JSON file as the first command-line argument"
    Exit 1
}

$jsonContent = Get-Content -Path $PARAMS_FILE | ConvertFrom-Json

# Authenticate with GitHub
gh auth login

# Get the repository URL
$GH_URL = gh repo view --json url | ConvertFrom-Json | % { $_.url }

# Remove the 'https://github.com/' part
$GH_OWNER, $GH_REPO = ($GH_URL -replace 'https://github.com/', '') -split '/', 2

# Initialize service principal name and credentials
$previousSPName = $null
$clientId = $null
$clientSecret = $null
$tenantId = $null

foreach ($env in $jsonContent.PSObject.Properties.Name) {
    $envDetails = $jsonContent.$env

    # Extract the variables from the JSON content
    $SUBSCRIPTION_ID = $envDetails.subscription_id
    $SP_NAME = $envDetails.sp_name

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

    # Create or update the environment with the given configuration
    gh api -X PUT -H "Accept: application/vnd.github+json" "repos/$GH_OWNER/$GH_REPO/environments/$env"
     
    # Store the secrets
    gh secret set ARM_CLIENT_ID -r "$GH_OWNER/$GH_REPO" --body $clientId --env $env
    gh secret set ARM_CLIENT_SECRET -r "$GH_OWNER/$GH_REPO" --body $clientSecret --env $env
    gh secret set ARM_TENANT_ID -r "$GH_OWNER/$GH_REPO" --body $tenantId --env $env
}