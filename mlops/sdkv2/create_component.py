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

def parse_default_values(component_inputs, references):
    inputs_with_defaults = {}
    print("component_inputs:", component_inputs")
    print("references:", references)
    for input_name, input_properties in component_inputs.items():
        print(f"Processing input '{input_name}' with properties: {input_properties}")
        if isinstance(input_properties, dict):
            if 'default' in input_properties:
                # If the 'default' field is present in the component input, use it
                default_value = input_properties['default']
                print(f"Default value for '{input_name}' found in the component input: {default_value}")
            else:
                # Otherwise, find the referenced type and use its default value
                ref_key = input_properties['reference']
                default_value = references.get(f'{ref_key}.default')
                print(f"Default value for '{input_name}' found in the references: {default_value}")

            # Add the input properties to the result, including the parsed default value
            inputs_with_defaults[input_name] = {**input_properties, 'default': default_value}
            print(f"Final input properties for '{input_name}': {inputs_with_defaults[input_name]}")
        else:
            # If the input_properties is not a dictionary, just use it as is
            inputs_with_defaults[input_name] = input_properties
            print(f"Input properties for '{input_name}' is not a dictionary. Using as is: {inputs_with_defaults[input_name]}")

    return inputs_with_defaults



def create_component_from_json(component, references):
    print("REFERENCES:", references)

    # Look up the full properties of each input type from the references
    component_inputs = {
        name: references.get(f'input_and_output_types.{input_type}') 
        for name, input_type in component['inputs'].items()
    }
    print("component_inputs:", component_inputs)

    inputs = parse_default_values(component_inputs, references)

    outputs = {
        k: Output(type=references.get(v, None)) 
        if isinstance(v, str) else Output(type=references.get(v['reference'], None)) 
        for k, v in component['outputs'].items()
    }

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

    print("component_inputs:", component_inputs)
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
