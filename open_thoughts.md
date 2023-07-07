# Open thoughts & ideas (Not implemented)   
<!-- To switch between views, press Ctrl+Shift+V in the editor. You can view the preview side-by-side (Ctrl+K V) with the file you are editing and see changes reflected in real-time as you edit. -->
This file is temporary and to be used as a way to note down different thoughts and ideas in one place.
Below are the current topics, (@GrannyProgramming means these should be implemented asap)
- @Security
- @workflow
- @Permission
- @environment
- @component
- @

## Github workflow @workflow 
#### Concurrency
When you're working on a feature branch and pushing multiple commits. You may not want to run workflows for every single commit if those commits are rapidly superseded by newer ones. With the concurrency field, only the workflow for the latest commit will run.

```yaml
concurrency: 
  group: ${{ github.workflow }}-${{ github.event.pull_request.number || github.ref }}
  cancel-in-progress: true
```

#### One shot workflow v multistep workflows
For simple projects with a small team, a one-shot workflow might be sufficient and easier to manage. For larger, more complex projects or for larger teams, a multi-step workflow could offer more flexibility and efficiency. 

#### Using artifacts in an MLOps workflow
Artifacts play a vital role in Machine Learning Operations (MLOps) workflows. They help in ensuring reproducibility, version control, data sharing, model evaluation, deployment, testing, and maintaining a secure environment. Key best practices for using artifacts in MLOps include:

- Saving each trained model as an artifact for versioning and reproducibility.
- Storing metadata such as model parameters, code version, and performance metrics alongside the model.
- Using artifacts to share data across different steps in a multi-step MLOps workflow.
- Storing evaluation metrics as artifacts to track model performance over time.
- Deploying the model in production using model artifacts.
- Utilizing artifacts in integration tests to validate the model serving infrastructure.
- Implementing conditional artifact creation in complex workflows to save resources.
- Setting up a retention policy to manage artifact lifecycle.
- Securing model artifacts due to potential reverse-engineering risks.
- Storing models as artifacts when conducting A/B tests for future reproducibility.

## Additional Workflow Steps
#### Optional step to create Vnet via cli @Security
**ensure_vnet()**: This function takes up to two arguments. The first is the name of the vnet to create, and the second is the CIDR block to use for the vnet. If the arguments are not provided, the function will default to vnetName for the vnet name and the value of the VNET_CIDR environment variable for the CIDR block.
```bash
function ensure_vnet() {
    local VNET_NAME="${1:-vnetName}"
    local VNET_CIDR="${2:-${VNET_CIDR:-}}"
    vnet_exists=$(az network vnet list --resource-group "${RESOURCE_GROUP_NAME}" --query "[?name == '$VNET_NAME']" | tail -n1 | tr -d "[:cntrl:]")
    if [[ "${vnet_exists}" = "[]" ]]; then
       echo_info "creating $VNET_NAME vnet "
       az network vnet create --name "$VNET_NAME" --address-prefixes "$VNET_CIDR" > /dev/null
       echo_info "vnet $VNET_NAME creation completed"
    else
       echo_warning "vnet $VNET_NAME already exists. reusing pre-created one"
    fi
}
```
**ensure_subnet:** This function takes up to three arguments. The first is the name of the vnet within which to create the subnet, the second is the name of the subnet to create, and the third is the CIDR block to use for the subnet. If the arguments are not provided, the function defaults to vnetName for the vnet name, mastersubnet for the subnet name, and the value of the MASTER_SUBNET environment variable for the CIDR block.

```bash
function ensure_subnet() {
    local VNET_NAME="${1:-vnetName}"
    local MASTER_SUBNET_NAME="${2:-mastersubnet}"
    local MASTER_SUBNET="${3:-${MASTER_SUBNET:-}}"
    subnet_exists=$(az network vnet subnet list --resource-group "${RESOURCE_GROUP_NAME}" --vnet-name "$VNET_NAME" --query "[?name == '$MASTER_SUBNET_NAME']" | tail -n1 | tr -d "[:cntrl:]")
    if [[ "${subnet_exists}" = "[]" ]]; then
       echo_info "creating master subnet: $MASTER_SUBNET_NAME"
       az network vnet subnet create --vnet-name "$VNET_NAME" --name "$MASTER_SUBNET_NAME" --address-prefixes "$MASTER_SUBNET" > /dev/null
       echo_info "subnet $MASTER_SUBNET_NAME creation completed"
    else
       echo_warning "subnet $MASTER_SUBNET_NAME already exists. reusing pre-created one"
    fi
}
```
#### Create a shared registry @GrannyProgramming @environment
Do we need logic to set up shared registry? I believe we should have it as an option in intial setup.
An Azure Machine Learning workspace does not automatically create a registry. Hence the below two functions are needed.
**ensure_registry_local:** This function first checks if a registry (identified by LOCAL_REGISTRY_NAME) exists in the provided resource group. If the registry does not exist, it attempts to create a new one.
```bash
function ensure_registry(){
    local LOCAL_REGISTRY_NAME="${1:-${REGISTRY_NAME:-}}"
    registry_exists=$(az ml registry list --resource-group "${RESOURCE_GROUP_NAME}" --query "[?name == '$LOCAL_REGISTRY_NAME']" |tail -n1|tr -d "[:cntrl:]")
    if [[ "${registry_exists}" = "[]" ]]; then
        retry_times=0
        while true 
        do 
            retry_times=$((retry_times+1))
            ensure_registry_local
            if [[ $? -ne 0 ]]; then
                if [[ $retry_times -gt 9 ]]; then
                    echo_error "Failed to create registry after 10 retries"
                    exit 1
                fi
                continue
            else 
                echo_info "registry ${LOCAL_REGISTRY_NAME} created successfully" >&2
                break
            fi
        done
    else
        echo_warning "registry ${LOCAL_REGISTRY_NAME} already exist, skipping creation step..." >&2
    fi
}
```

**ensure_registry_local:** This function again checks if the desired registry exists. If it does not, it repeatedly calls ensure_registry_local until it succeeds in creating the registry or until it has failed 10 times.
```bash
function ensure_registry_local(){
    registry_exists=$(az ml registry list --resource-group "${RESOURCE_GROUP_NAME}" --query "[?name == '$LOCAL_REGISTRY_NAME']" |tail -n1|tr -d "[:cntrl:]")
    if [[ "${registry_exists}" = "[]" ]]; then
        echo_info "registry ${LOCAL_REGISTRY_NAME} does not exist; creating" >&2
        sed -i "s/<REGISTRY-NAME>/$LOCAL_REGISTRY_NAME/" $SCRIPT_DIR/infra_resources/registry-demo.yml
        sed -i "s/<LOCATION>/$LOCATION/" $SCRIPT_DIR/infra_resources/registry-demo.yml
        cat $SCRIPT_DIR/infra_resources/registry-demo.yml
        az ml registry create --resource-group $RESOURCE_GROUP_NAME --file $SCRIPT_DIR/infra_resources/registry-demo.yml --name $LOCAL_REGISTRY_NAME || echo "Failed to create registry $LOCAL_REGISTRY_NAME, will retry"
        registry_exists=$(az ml registry list --resource-group "${RESOURCE_GROUP_NAME}" --query "[?name == '$LOCAL_REGISTRY_NAME']" |tail -n1|tr -d "[:cntrl:]")
        if [[ "${registry_exists}" = "[]" ]]; then
            echo_info "Retry creating registry ${LOCAL_REGISTRY_NAME}" >&2
            sleep 30
            return 1
        fi
    fi
    return 0
}
```
#### Permissions @permissions

**grant_permission_app_id_on_rg:** This function is used to assign the 'Storage Blob Data Owner' role to a specific service principal on a specific resource group in Azure. The role 'Storage Blob Data Owner' grants full access to Azure Storage blob containers and data. The permissions include reading, writing, and deleting blobs in all blob containers in the storage account.
```bash
function grant_permission_app_id_on_rg() {
    local SERVICE_PRINCIPAL_NAME="${1:-APP_NAME}"
    servicePrincipalAppId=$(az ad sp list --display-name "${SERVICE_PRINCIPAL_NAME}" --query "[].appId" -o tsv | tail -n1 | tr -d "[:cntrl:]")
    RESOURCE_GROUP_ID=$(az group show --name "${RESOURCE_GROUP_NAME}" --query id -o tsv | tail -n1 | tr -d "[:cntrl:]")
    cmd="az role assignment create --role 'Storage Blob Data Owner' --assignee $servicePrincipalAppId --scope $RESOURCE_GROUP_ID"
    eval "$cmd"
}
```
**grant_permission_identity_on_acr:** This function is used to grant an Azure Managed Identity the 'Contributor' and 'AcrPull' roles on an Azure Container Registry (ACR).
```bash
function grant_permission_identity_on_acr() {
    local IDENTITY_NAME="${1:-identity}"
    Id=$(az identity list --query "[?name=='$IDENTITY_NAME'].principalId" -o tsv)
    if [[ -z $Id ]]; then
        echo_warning "Managed Identity: $IDENTITY_NAME does not exists."
    fi
    az role assignment create --role "Contributor" --assignee-object-id "$Id"  --assignee-principal-type ServicePrincipal &> /dev/null
    az role assignment create --role "AcrPull" --assignee-object-id "$Id"  --assignee-principal-type ServicePrincipal &> /dev/null
}
```


## Components @components
In Azure Machine Learning, components are modular building blocks that encapsulate a specific task or functionality within a machine learning workflow. They provide a way to package and reuse code, data, and dependencies, making it easier to develop, manage, and scale machine learning pipelines. Here is a summary of the components in Azure Machine Learning:

**Command Component:** Represents a command-line executable or script that can be executed as a step in a pipeline. It allows you to define inputs, outputs, environment settings, and command arguments.

#### Compare two models (CLI)
These scripts only compare two different models  that have only been implemented in the script, they are xplicitly stated. I would like to ammend this so that it will compare the most recent model against the best/latest model in AML. If it is indeed better, I want it to save all components used into the AML environment. This script is  a good starting point for [this](https://github.com/Azure/azureml-examples/tree/main/cli/jobs/pipelines-with-components/pipeline_with_pipeline_component/pipeline_with_train_eval_pipeline_component). 

The provided Python script and YAML file define a command component in Azure Machine Learning that performs a comparison between two models. The Python script takes input paths for the models and their evaluation results, performs the comparison, and writes the results to specified output paths. The YAML file specifies the component's properties, including its name, description, inputs, outputs, environment, code location, and command. By combining the Python script and YAML file, you can create a reusable component that can be incorporated into machine learning workflows in Azure Machine Learning.

```yaml
$schema: https://azuremlschemas.azureedge.net/latest/commandComponent.schema.json
type: command

name: compare_2_models
display_name: Compare 2 Models
description: A dummy comparison module takes two models as input and outputs the better one
inputs:
  model1:
    type: uri_folder
  eval_result1:
    type: uri_folder
  model2:
    type: uri_folder
  eval_result2:
    type: uri_folder
outputs:
  best_model:
    type: uri_folder
  best_result:
    type: uri_folder
environment: azureml://registries/azureml/environments/AzureML-sklearn-0.24-ubuntu18.04-py37-cpu
code: .
command: >-
  python compare2.py 
  --model1 ${{inputs.model1}}
  --eval_result1 ${{inputs.eval_result1}}
  --model2 ${{inputs.model2}}
  --eval_result2 ${{inputs.eval_result2}}
  --best_model ${{outputs.best_model}}
  --best_result ${{outputs.best_result}}
```

The Python script performs a comparison between two models. It takes several command-line arguments representing the input models, evaluation results, and outputs. It then writes the comparison results to the specified output paths. 

```python
import argparse
from pathlib import Path

parser = argparse.ArgumentParser("compare2")
parser.add_argument("--model1", type=str, help="The first model to compare with")
parser.add_argument(
    "--eval_result1", type=str, help="The evaluation result of first model"
)
parser.add_argument("--model2", type=str, help="The second model to compare")
parser.add_argument(
    "--eval_result2", type=str, help="The evaluation result of second model"
)
parser.add_argument("--best_model", type=str, help="The better model among the two")
parser.add_argument(
    "--best_result", type=str, help="The better model evalution result among the two"
)


args = parser.parse_args()

lines = [
    f"Model #1: {args.model1}",
    f"Evaluation #1: {args.eval_result1}",
    f"Model #2: {args.model2}",
    f"Evaluation #2: {args.eval_result2}",
    f"Best model path: {args.best_model}",
]

Path(args.best_model).mkdir(parents=True, exist_ok=True)
model_output = Path(args.best_model) / Path("model").name
with open(model_output, "w") as file:
    for line in lines:
        print(line)
        file.write(line + "\n")

Path(args.best_result).mkdir(parents=True, exist_ok=True)
result_output = Path(args.best_result) / Path("result").name
with open(result_output, "w") as file:
    for line in lines:
        print(line)
        file.write(line + "\n")
```