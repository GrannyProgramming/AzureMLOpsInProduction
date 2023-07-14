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
                        # If the referenced value is a string, take the last part of the reference key
                        data[key] = ref_value.split('.')[-1]
                    else:
                        # If the referenced value is not a string, use it directly
                        data[key] = ref_value
                else:
                    replace_references(value, references)
    elif isinstance(data, list):
        for item in data:
            replace_references(item, references)
    return data


def create_component_from_json(component, references):
    print("REFERENCES:", references)

    inputs = {}

    for k, v in component['inputs'].items():
        default_value = None  # Initialize default_value
        input_type = None

        if isinstance(v, str):
            input_type = references[f'input_and_output_types.{v}.type']
        else:
            input_def = references.get(f'components_framework.{component["name"]}.inputs.{k}')
            if input_def and 'reference' in input_def:
                ref_key = input_def['reference']
                input_type = references[f'{ref_key}.type']

                # Check 1: Extract default from 'components_framework' inside 'inputs'
                if 'default' in input_def:
                    default_value = input_def['default']

        # If default_value is still None, try another way to get it
        if default_value is None:
            # Check 2: Try getting the default value directly from 'input_and_output_types'
            default_value = references.get(f'input_and_output_types.{v}.default')
            # Check 3: Try getting the default value directly from 'components_framework' but outside 'inputs'
            if default_value is None:
                default_value = references.get(f'components_framework.{component["name"]}.inputs.{k}.default')

        if default_value is not None:
            # Convert the default value to the correct type
            if input_type == 'number':
                default_value = float(default_value)
            elif input_type == 'integer':
                default_value = int(default_value)
            elif input_type == 'boolean':
                default_value = bool(default_value)

        print(f"Default value for {k}: {default_value}")

        if input_type in ["string", "integer", "number", "boolean"]:
            inputs[k] = Input(type=input_type, default=default_value)
        else:
            inputs[k] = Input(type=input_type)

    print("INPUTS:", inputs)



    outputs = {k: Output(type=references.get(v, None)) if isinstance(v, str) else Output(type=references.get(v['reference'], None)) for k, v in component['outputs'].items()}  
    command_str = f'python {component["filepath"]} ' + ' '.join(f"--{name} ${{{{{f'inputs.{name}'}}}}}" for name in component['inputs']) + ' ' + ' '.join(f"--{name} ${{{{{f'outputs.{name}'}}}}}" for name in component['outputs'])
    code_filepath = references['component_filepaths.base_path'] + component['filepath']
    environment = references[f'environments.{component["env"]}.env']  # Use the environment from the references
    display_name = ' '.join(word.capitalize() for word in component['name'].split('_'))
    
    new_component = command(
        name=component['name'],
        display_name=display_name,
        inputs=inputs,
        outputs=outputs,
        code=code_filepath,
        command=command_str,
        environment=environment
    )

    print("new_component variable: ", new_component)
    return new_component


def create_components_from_json_file(json_file):
    with open(json_file) as f:
        data = json.load(f)

    references = generate_references(data)
    
    print("REFERENCES:", references)

    resolved_json = replace_references(copy.deepcopy(data), references)

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
client = initialize_mlclient()
# for component in components:
#     compare_and_update_component(client, component)
