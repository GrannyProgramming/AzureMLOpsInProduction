import sys
import yaml
from azure.ai.ml import command
from azure.ai.ml import Input, Output
from workflowhelperfunc.workflowhelper import initialize_mlclient
import os

def create_component_from_yaml(component_name, component_data, tag_value):
    inputs = {}
    for k, v in component_data['inputs'].items():
        input_type = v.get('type', None)
        default_value = v.get('default', None)
        inputs[k] = Input(type=input_type, default=default_value)

    outputs = {}
    for k, v in component_data['outputs'].items():
        output_type = v.get('type', None)
        outputs[k] = Output(type=output_type)

    command_str = 'python ' + ' '.join(f"--{name} ${{{{{f'inputs.{name}'}}}}}" for name in component_data['inputs']) + ' ' + ' '.join(f"--{name} ${{{{{f'outputs.{name}'}}}}}" for name in component_data['outputs'])
    code_filepath = component_data.get('code', '')
    environment = component_data.get('environment', '')
    display_name = component_data.get('display_name', '')

    new_component = command(
        name=component_name,
        display_name=display_name,
        inputs=inputs,
        outputs=outputs,
        code=code_filepath,
        command=command_str,
        environment=environment,
        tags={"folder": tag_value}
    )
    print(new_component)
    return new_component

def create_components_from_yaml_file(yaml_file):
    with open(yaml_file, 'r') as f:
        data = yaml.safe_load(f)

    # Get the directory name
    dirname = os.path.basename(os.path.dirname(yaml_file))

    components = [create_component_from_yaml(component_data['name'], component_data, dirname) 
                  for component_data in data['components'].values()]
    return components

def compare_and_update_component(client, component):
    try:
        azure_component = next((comp for comp in client.components.list() if comp.name == component.name), None)
        if azure_component:
            azure_component = client.components.get(name=azure_component.name, version=azure_component.latest_version)
        if azure_component.inputs == component.inputs and azure_component.outputs == component.outputs and azure_component.command == component.command:
            print(f"Component {component.name} with Version {component.version} already exists and is identical. No update required.")
        else:
            print(f"Component {component.name} differs from AML version. Updating component.")
            print(component.component)
            updated_component = client.create_or_update(component.component)
            print(f"Updated Component {updated_component.name} with Version {updated_component.version}")
    except Exception as e:
        print(f"Component {component.name} does not exist. Creating component.")
        new_component = client.create_or_update(component.component)
        print(f"Created Component {new_component.name} with Version {new_component.version}")

yaml_file = sys.argv[1]
components = create_components_from_yaml_file(yaml_file)
client = initialize_mlclient()
for component in components:
    compare_and_update_component(client, component)
