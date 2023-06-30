import sys
import json
import copy
from azure.ai.ml import command
from azure.ai.ml import Input, Output
from workflowhelperfunc.workflowhelper import initialize_mlclient

def replace_references(data, original):
    if isinstance(data, dict):
        if 'reference' in data:
            parts = data['reference'].split('.')
            ref_data = original
            for part in parts:
                ref_data = ref_data[part]
            return ref_data
        else:
            new_dict = {}
            for key, value in data.items():
                new_dict[key] = replace_references(value, original)
            return new_dict
    elif isinstance(data, list):
        return [replace_references(item, original) for item in data]
    else:
        return data

def create_component_from_json(component):
    inputs = {k: Input(type=v['type']) for k, v in component['inputs'].items()}  # assuming type is a string
    outputs = {k: Output(type=v['type']) for k, v in component['outputs'].items()}  # assuming type is a string

    new_component = command(
        name=component['name'],
        display_name=component['display_name'],
        inputs=inputs,
        outputs=outputs,
        code=component['code_filepath'],
        command=component['command'],  # actual command should be the value
        environment=component['environment'],  # reference replaced with actual environment
    )

    return new_component

def create_components_from_json_file(json_file):
    with open(json_file, 'r') as f:
        data = json.load(f)

    # Create a deep copy of the original json data to not modify the original structure
    json_copy = copy.deepcopy(data)

    # Replace all the references
    resolved_json = replace_references(json_copy, data)

    components = [create_component_from_json(component) for component in resolved_json['components']]

    return components

# use the function to create components
json_file = sys.argv[1]  # get json filepath from command line argument
components = create_components_from_json_file(json_file)

# Assuming you have ml_client instance

for component in components:
    client=initialize_mlclient()
    component = client.create_or_update(component.component)
    print(
        f"Component {component.name} with Version {component.version} is registered"
    )
