import sys
import yaml
from azure.ai.ml import command
from azure.ai.ml import Input, Output
from workflowhelperfunc.workflowhelper import initialize_mlclient
import os

def create_component_from_yaml(component_name, component_data, tag_value):
    inputs = {k: Input(type=v.get('type', None), default=v.get('default', None)) for k, v in component_data['inputs'].items()}
    outputs = {k: Output(type=v.get('type', None)) for k, v in component_data['outputs'].items()}

    command_str = 'python ' + ' '.join(f"--{name} ${{{{{f'inputs.{name}'}}}}}" for name in inputs.keys()) + ' ' + ' '.join(f"--{name} ${{{{{f'outputs.{name}'}}}}}" for name in outputs.keys())
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
    
    # Debug print statement
    print(data)
    
    dirname = os.path.basename(os.path.dirname(yaml_file))
    
    components_data = data.get('components')
    if components_data is None:
        print("No 'components' key in data")
        return []
    
    components = [create_component_from_yaml(name, comp, dirname) for name, comp in components_data.items()]
    return components

def compare_and_update_component(client, component):
    try:
        azure_component = next((comp for comp in client.components.list() if comp.name == component.name), None)
        if azure_component:
            azure_component = client.components.get(name=azure_component.name, version=azure_component.latest_version)

        if azure_component and azure_component.inputs == component.inputs and azure_component.outputs == component.outputs and azure_component.command == component.command:
            print(f"Component {component.name} with Version {component.version} already exists and is identical. No update required.")
        else:
            updated_component = client.create_or_update(component.component)
            print(f"{'Updated' if azure_component else 'Created'} Component {updated_component.name} with Version {updated_component.version}")
    except Exception as e:
        print(f"Error in {e} while updating/creating the component {component.name}.")

yaml_file = sys.argv[1]
components = create_components_from_yaml_file(yaml_file)
client = initialize_mlclient()
for component in components:
    compare_and_update_component(client, component)
