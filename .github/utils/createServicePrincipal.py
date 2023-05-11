import os
import subprocess
import json

# Ensure Azure CLI is installed
assert subprocess.run(["az", "--version"], capture_output=True).returncode == 0, "Azure CLI not installed"

# Ensure environment variables are set
assert "SUBSCRIPTION_ID" in os.environ, "SUBSCRIPTION_ID environment variable not set"
assert "SP_NAME" in os.environ, "SP_NAME environment variable not set"
assert "GH_TOKEN" in os.environ, "GH_TOKEN environment variable not set"
assert "GH_OWNER" in os.environ, "GH_OWNER environment variable not set"
assert "GH_REPO" in os.environ, "GH_REPO environment variable not set"

subscription_id = os.environ["SUBSCRIPTION_ID"]
sp_name = os.environ["SP_NAME"]
gh_token = os.environ["GH_TOKEN"]
gh_owner = os.environ["GH_OWNER"]
gh_repo = os.environ["GH_REPO"]

# Set the subscription id
subprocess.run(["az", "account", "set", "--subscription", subscription_id], check=True)

# Create the service principal
sp_create_output = subprocess.run(
    ["az", "ad", "sp", "create-for-rbac", "-n", sp_name, "--skip-assignment"],
    capture_output=True,
    check=True,
    text=True,
)

# Parse the json output
sp_create_output_json = json.loads(sp_create_output.stdout)

# Get the appId, password, and tenant
app_id = sp_create_output_json["appId"]
password = sp_create_output_json["password"]
tenant_id = sp_create_output_json["tenant"]

print(f"Created service principal with appId: {app_id}")

# Log in to Azure with the service principal
subprocess.run(
    ["az", "login", "--service-principal", "-u", app_id, "-p", password, "--tenant", tenant_id],
    check=True,
)

# Create GitHub secrets for appId, password, tenant id, subscription id, and the full output
for secret_name, secret_value in {"AZURE_CLIENT_ID": app_id, "AZURE_TENANT_ID": tenant_id, "AZURE_SUBSCRIPTION_ID": subscription_id, "AZURE_SECRET": password, "AZURE_CREDENTIALS": json.dumps(sp_create_output_json)}.items():
    subprocess.run(
        [
            "curl",
            "-X",
            "PUT",
            f"https://api.github.com/repos/{gh_owner}/{gh_repo}/actions/secrets/{secret_name}",
            "-H",
            "Accept: application/vnd.github.v3+json",
            "-H",
            f"Authorization: token {gh_token}",
            "-d",
            json.dumps({"encrypted_value": secret_value, "key_id": gh_token}),
        ],
        check=True,
    )
