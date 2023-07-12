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
        if isinstance(value, dict):
            # If the value is a type definition or an environment definition, add it as a reference as a whole
            if ('type' in value and not isinstance(value['type'], dict)) or 'env' in value:
                references[full_key] = value
            else:
                references.update(generate_references(value, full_key))
        else:
            references[full_key] = value
    return references

def replace_references(data, references):
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, dict) and 'reference' in value:
                if value['reference'] in references:
                    data[key] = references[value['reference']]
                else:
                    raise ValueError(f"Reference '{value['reference']}' not found.")
            else:
                replace_references(value, references)
    elif isinstance(data, list):
        for item in data:
            replace_references(item, references)
    return data

def create_component_from_json(component, references):
    inputs = {k: Input(type=v['type'], default=v.get('default', None)) for k, v in component['inputs'].items()}  
    outputs = {k: Output(type=v['type']) for k, v in component['outputs'].items()}  
    command_str = 'python {component["filepath"]} ' + ' '.join("--{name} ${{{{{inputs.{name}}}}}}" for name in component['inputs']) + ' ' + ' '.join("--{name} ${{{outputs.{name}}}}" for name in component['outputs'])
    code_filepath = references['component_filepaths.base_path'] + component['filepath']
    environment = component['env']['env']
    display_name = ' '.join(word.capitalize() for word in component['name'].split('_'))
    new_component = command(
        name=component['name'],
        display_name=display_name,
        inputs=inputs,
        outputs=outputs,
        code=code_filepath,
        command=command_str,
        environment=environment,
    )
    return new_component

def create_components_from_json_file(json_file):
    with open(json_file, 'r') as f:
        data = json.load(f)
    references = generate_references(data)
    print(references)
    resolved_json = replace_references(copy.deepcopy(data), references)
    print(resolved_json)
    components = [create_component_from_json(component, references) for component in resolved_json['components_framework'].values()]
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
            updated_component = client.create_or_update(component)
            print(f"Updated Component {updated_component.name} with Version {updated_component.version}")
    except Exception as e:
        print(f"Component {component.name} with Version {component.version} does not exist. Creating component.")
        new_component = client.create_or_update(component)
        print(f"Created Component {new_component.name} with Version {new_component.version}")

json_file = sys.argv[1]
components = create_components_from_json_file(json_file)
client = initialize_mlclient()
for component in components:
    compare_and_update_component(client, component)
