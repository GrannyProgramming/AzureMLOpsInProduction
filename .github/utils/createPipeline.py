import json
from azure.ai.ml import MLClient
from azure.ai.ml.entities import Pipeline, PipelineStep, ComponentReference
from azure.identity import DefaultAzureCredential

# Load credentials
credential = DefaultAzureCredential()

# Load client
client = MLClient(credential, subscription_id='<your-subscription-id>', resource_group_name='<your-resource-group>', workspace_name='<your-workspace>')

# Load JSON data
with open('pipelines.json') as f:
    pipelines_data = json.load(f)['pipelines']

# Create pipelines
for pipeline_name, data in pipelines_data.items():
    components = [PipelineStep(name=comp_name, component=ComponentReference(comp_name)) for comp_name in data['components']]

    pipeline = Pipeline(name=data['name'], description=data['description'], version=data['version'], steps=components)

    # Save pipeline
    client.pipelines.create_or_update(pipeline)
