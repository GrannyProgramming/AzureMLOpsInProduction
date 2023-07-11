import sys
import json
import copy
from azure.ai.ml import command
from azure.ai.ml import Input, Output
from workflowhelperfunc.workflowhelper import initialize_mlclient

def generate_references(data):
    references = {}
    for key, value in data.items():
        if isinstance(value, dict):
            for subkey, subvalue in value.items():
                references[f"{key}.{subkey}"] = subvalue
        else:
            references[key] = value
    return references

def replace_references(data, original):
    if isinstance(data, dict):
        if 'reference' in data and isinstance(data['reference'], str):
            parts = data['reference'].split('.')
            ref_data = original
            for part in parts:
                if isinstance(ref_data, dict) and part in ref_data:
                    ref_data = ref_data.get(part)
                else:
                    ref_data = data  # Return the original dictionary if the reference cannot be resolved
                    break
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

def create_component_from_json(component, references):
    print("Creating component", component["name"])
    print("Component inputs:", component["inputs"])
    print("Component outputs:", component["outputs"])

    # Generate display_name from name
    display_name = component['name'].replace('_', ' ').title()

    # Resolve references for inputs and outputs
    inputs = {k: Input(type=references[v['reference']]['type'], default=v.get('default', None)) for k, v in component['inputs'].items()}  
    outputs = {k: Output(type=references[v['reference']]['type']) for k, v in component['outputs'].items()}  

    # generate command string
    command_inputs = ' '.join('--{name} ${{{{{inputs.{name}}}}}}' if not references[v['reference']].get('optional', False) else '$[[--{name} ${{{{inputs.{name}}}}]]' for name, v in component['inputs'].items())
    command_outputs = ' '.join('--{name} ${{{outputs.{name}}}}' for name in outputs.keys())
    command_str = f'python {component["filepath"]} {command_inputs} {command_outputs}'

    # concatenate base path with relative path
    code_filepath = references['component_filepaths.base_path'] + component['filepath']

    new_component = command(
        name=component['name'],
        display_name=display_name,
        inputs=inputs,
        outputs=outputs,
        code=code_filepath,
        command=command_str,  # actual command should be the value
        environment=component['env'],  # reference replaced with actual environment
    )

    return new_component



def create_components_from_json_file(json_file):
    with open(json_file, 'r') as f:
        data = json.load(f)

    # Create a deep copy of the original json data to not modify the original structure
    json_copy = copy.deepcopy(data)

    # Generate references from JSON root
    references = generate_references(json_copy)

    # Replace all the references
    resolved_json = replace_references(json_copy, references)

    components = [create_component_from_json(component, references) for component in resolved_json['components_framework'].values()]

    return components

def compare_and_update_component(client, component):
    try:
        # Retrieve existing component
        azure_component = client.get_component(component.name, component.version)

        # Compare schemas
        if azure_component.get_schema() == component.get_schema():
            print(f"Component {component.name} with Version {component.version} already exists and has same schema. No update required.")
        else:
            print(f"Component {component.name} with Version {component.version} schema differs. Updating component.")
            updated_component = client.create_or_update(component)
            print(f"Updated Component {updated_component.name} with Version {updated_component.version}")
    except Exception as e:
        # If component does not exist, create new component
        print(f"Component {component.name} with Version {component.version} does not exist. Creating component.")
        new_component = client.create_or_update(component)
        print(f"Created Component {new_component.name} with Version {new_component.version}")

# use the function to create components
json_file = sys.argv[1]  # get json filepath from command line argument
components = create_components_from_json_file(json_file)

# Initialize Azure ML client
client = initialize_mlclient()

# Iterate over all components and compare/update them
for component in components:
    compare_and_update_component(client, component)
