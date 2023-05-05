import json
import subprocess

# Get the Azure subscription ID from an environment variable
subscription_id = subprocess.check_output(['bash', '-c', 'echo $AZURE_SUBSCRIPTION_ID']).decode().strip()
sp_name = subprocess.check_output(['bash', '-c', 'echo "amcgsp" $ENVIRONMENT']).decode().strip()
# Check if the service principal already exists
result = subprocess.run([
    'az', 'ad', 'sp', 'show',
    '--id', '{sp_name}'
], capture_output=True, text=True)
if result.returncode == 0:
    # The service principal already exists, so check if its credentials are stored in GitHub secrets
    existing_secrets = {}
    for name in ['AZURE_CLIENT_ID', 'AZURE_CLIENT_SECRET', 'AZURE_TENANT_ID']:
        try:
            value = subprocess.check_output(['bash', '-c', f'gh secret get {name} --repo myusername/my-repo --silent'], text=True)
            existing_secrets[name] = value.strip()
        except subprocess.CalledProcessError:
            pass

    if len(existing_secrets) == 3:
        # All three secrets are already set, so exit without creating a new service principal
        print('Service principal already exists and secrets are set')
        exit(0)

# Create a service principal with a random password
result = subprocess.run([
    'az', 'ad', 'sp', 'create-for-rbac',
    '--role', 'Contributor',
    '--scopes', f'/subscriptions/{subscription_id}',
    '--name', f'{sp_name}',
    '--query', '{clientId: appId, clientSecret: password, tenantId: tenant}'
], capture_output=True, text=True)

# Parse the output and store the credentials in GitHub secrets
output = json.loads(result.stdout)
secrets = {
    'AZURE_CLIENT_ID': output['clientId'],
    'AZURE_CLIENT_SECRET': output['clientSecret'],
    'AZURE_TENANT_ID': output['tenantId']
}
for name, value in secrets.items():
    subprocess.run(['bash', '-c', f'echo "{value}" | gh secret set {name} --repo $gh_address --silent'])
