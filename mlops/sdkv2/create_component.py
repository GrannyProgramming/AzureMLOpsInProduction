import sys
import json
import copy
from azure.ai.ml import command
from azure.ai.ml import Input, Output
from workflowhelperfunc.workflowhelper import initialize_mlclient

def generate_references(data, parent_key=''):
    references = {}
    for key, value in data.items():
        full_key = f"{parent_key}.{key}" if parent_key else key
        if isinstance(value, dict) and not 'reference' in value:
            references.update(generate_references(value, full_key))
        else:
            references[full_key] = value
    return references

def replace_references(data, references):
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, dict):
                if 'reference' in value:
                    ref_key = value['reference']
                    ref_value = references.get(ref_key, value['reference'])
                    if isinstance(ref_value, str):
                        data[key] = ref_value.split('.')[-1]
                    else:
                        data[key] = ref_value
                else:
                    replace_references(value, references)
    elif isinstance(data, list):
        for item in data:
            replace_references(item, references)
    return data

def parse_default_values(component_inputs, references):
    inputs_with_defaults = {}
    for input_name, input_properties in component_inputs.items():
        if isinstance(input_properties, dict):
            if 'reference' in input_properties:
                ref_key = input_properties['reference']
                default_value = references.get(f'{ref_key}.default', None)
                if 'default' in input_properties:
                    default_value = input_properties['default']
            else:
                default_value = None
            inputs_with_defaults[input_name] = {**input_properties, 'default_value': default_value}
        else:
            ref_key = input_properties
            default_value = references.get(f'{ref_key}.default')
            inputs_with_defaults[input_name] = {'type': input_properties, 'default_value': default_value}
    return inputs_with_defaults

def create_component_from_json(component, references):
    inputs = parse_default_values(component['inputs'], references)
    outputs = {k: references.get(v, None) if isinstance(v, str) else references.get(v['reference'], None) for k, v in component['outputs'].items()}  
    command_str = f'python {component["filepath"]} ' + ' '.join(f"--{name} ${{{{{f'inputs.{name}'}}}}}" for name in component['inputs']) + ' ' + ' '.join(f"--{name} ${{{{{f'outputs.{name}'}}}}}" for name in component['outputs'])
    code_filepath = references['component_filepaths.base_path'] + component['filepath']
    environment = references[f'environments.{component["env"]}.env']
    display_name = ' '.join(word.capitalize() for word in component['name'].split('_'))
    
    new_component = {
        'name': component['name'],
        'display_name': display_name,
        'inputs': inputs,
        'outputs': outputs,
        'code': code_filepath,
        'command': command_str,
        'environment': environment
    }

    return new_component


def create_components_from_json_file(json_file):
    with open(json_file) as f:
        json_data = json.load(f)

    # Generate the references
    references = generate_references(json_data)

    # Replace references in the JSON data
    resolved_json = replace_references(copy.deepcopy(json_data), references)

    # Create the components
    components = [create_component_from_json(c, references) for c in resolved_json['components_framework'].values()]

    return components

def compare_and_update_component(client, component):
    try:
        azure_component = next((comp for comp in client.components.list() if comp.name == component.name), None)
        if azure_component:
            azure_component = client.components.get(name=azure_component.name, version=azure_component.latest_version)
        if azure_component.inputs == component.inputs and azure_component.outputs == component.outputs and azure_component.command == component.command:
            print(f"Component {component.name} with Version {component.version} already exists and is identical. No update required.")
        else:
            print(f"Component {component.name} with Version {component.version} differs. Updating component.")
            updated_component = client.create_or_update(component.component)
            print(f"Updated Component {updated_component.name} with Version {updated_component.version}")
    except Exception as e:
        print(f"Component {component.name} with Version {component.version} does not exist. Creating component.")
        new_component = client.create_or_update(component.component)
        print(f"Created Component {new_component.name} with Version {new_component.version}")

json_file = sys.argv[1]
components = create_components_from_json_file(json_file)
# client = initialize_mlclient()
# for component in components:
#     compare_and_update_component(client, component)
