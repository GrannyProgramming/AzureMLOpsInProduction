from azure.identity import DefaultAzureCredential
from azure.ai.ml import MLClient
from azure.ai.ml.dsl import pipeline, PipelineParameter
from createComponents import prep_component


subscription_id = "e62983d6-29cb-4435-b8d2-b19887c7a735"
resource_group = "clitesting"
workspace = "clitest-amcg"

# Initialize MLClient
credential = DefaultAzureCredential()
ml_client = MLClient(credential, subscription_id, resource_group, workspace)

# Get the latest version of the data asset
# Note: the VERSION was set in a previous cell.
nyc_data = ml_client.data.get(name="green_yellow_taxi_data", version="latest")

# Define a pipeline containing 3 nodes: Prepare data node, train node, and score node
@pipeline(default_compute="cpu-cluster001")
def image_classification_keras_minist_convnet(pipeline_input_data: Input[str]):
    """E2E image classification pipeline with keras using python sdk."""
    prepare_data_node = prep_component(raw_data=pipeline_input_data)

# Create a pipeline
pipeline_job = image_classification_keras_minist_convnet(
    PipelineParameter(name="pipeline_input_data", value=nyc_data)
)

# Create or update a job to execute the pipeline
pipeline_job = ml_client.jobs.create_or_update(
    pipeline_job, experiment_name="pipeline_test"
)

# Wait until the job completes
ml_client.jobs.stream(pipeline_job.name)

# Register component
component_name = "prep_component"
component_version = "1"

try:
    # Try to get back the component
    prep = ml_client.components.get(name=component_name, version=component_version)
except:
    # If not exists, register the component
    prep = ml_client.components.create_or_update(
        prep_component, name=component_name, version=component_version
    )

# List all components registered in the workspace
for c in ml_client.components.list():
    print(c)
