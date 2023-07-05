import sys
import json
from azure.ai.ml.dsl import pipeline
from azure.ai.ml import load_component, Input
from workflowhelperfunc.workflowhelper import initialize_mlclient
import inspect

def load_component_by_name(name):
    existing_component = next((component for component in ml_client.components.list() 
                            if component.name == name), None)
    
    if existing_component:
        existing_component = ml_client.components.get(name=existing_component.name, 
                                                        version=existing_component.latest_version)
        component_func = load_component(client=ml_client, name=existing_component.name, version=existing_component.version)
    else:
        print(f"Component with name {name} does not exist.")
        component_func = None
    
    return component_func

@pipeline
def data_pipeline(raw_data: Input):
    prep_taxi_data = load_component_by_name('prep_taxi_data')
    if prep_taxi_data is None:
        return None
    prep_node = prep_taxi_data(raw_data=raw_data)

    taxi_feature_engineering = load_component_by_name('taxi_feature_engineering')
    if taxi_feature_engineering is None:
        return None
    transform_node = taxi_feature_engineering(clean_data=prep_node.outputs.prep_data)
    return {"train_data": transform_node.outputs.transformed_data}

@pipeline
def train_pipeline(train_data: Input, compute_train_node: str):
    train_linear_regression_model = load_component_by_name('train_linear_regression_model')
    if train_linear_regression_model is None:
        return None
    train_node = train_linear_regression_model(train_data=train_data)
    train_node.compute = compute_train_node

    predict_taxi_fares = load_component_by_name('predict_taxi_fares')
    if predict_taxi_fares is None:
        return None
    predict_node = predict_taxi_fares(
        model_input=train_node.outputs.model_output,
        test_data=train_node.outputs.test_data,
    )

    score_model = load_component_by_name('score_model')
    if score_model is None:
        return None
    score_node = score_model(
        predictions=predict_node.outputs.predictions,
        model=train_node.outputs.model_output,
    )
    return {
        "trained_model": train_node.outputs.model_output,
        "predictions": predict_node.outputs.predictions,
        "score_report": score_node.outputs.score_report,
    }

@pipeline
def nyc_taxi_data_regression(pipeline_raw_data: Input, compute_train_node: str):
    data_pipeline_node = data_pipeline(raw_data=pipeline_raw_data)
    if data_pipeline_node is None:
        return None
    train_pipeline_node = train_pipeline(
        train_data=data_pipeline_node.outputs.train_data,
        compute_train_node=compute_train_node,
    )
    if train_pipeline_node is None:
        return None
    return {
        "pipeline_job_trained_model": train_pipeline_node.outputs.trained_model,
        "pipeline_job_predictions": train_pipeline_node.outputs.predictions,
        "pipeline_job_score_report": train_pipeline_node.outputs.score_report,
    }

ml_client = initialize_mlclient()

json_file_path = sys.argv[1]

with open(json_file_path, 'r') as f:
    config = json.load(f)

for pipeline_config in config['pipelines']:
    components = [load_component_by_name(name) for name in pipeline_config['pipeline_components']]

    pipeline_job = nyc_taxi_data_regression(
        pipeline_raw_data=Input(type="uri_folder", path=pipeline_config['file_paths']['raw_data_path']),
        compute_train_node=pipeline_config['compute'],
    )

    if pipeline_job is None:
        print(f"Failed to create pipeline job for config: {pipeline_config}")
        continue

    pipeline_job.settings.default_compute = pipeline_config['compute']

    pipeline_job = ml_client.jobs.create_or_update(
        pipeline_job, experiment_name=f"{pipeline_config['name']}_with_pipeline_component"
    )
    print(pipeline_job)
