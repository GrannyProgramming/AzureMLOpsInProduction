import sys
import json
import copy
from azure.ai.ml import command
from azure.ai.ml import Input, Output

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

def create_component_from_json(component, references):

  inputs = {}
  for k, v in component['inputs'].items():
    if isinstance(v, str):
      # Reference
      type_reference = f'input_and_output_types.{v}.type'
      default_value = None 
    else:
      # Direct value
      type_reference = f'input_and_output_types.{v["reference"]}.type'
      
      # Look up default value from references
      default_value = references.get(f'components_framework.{component["name"]}.inputs.{k}.default', None)

    input_type = references.get(type_reference, None)
    inputs[k] = Input(type=input_type, default=default_value)

  outputs = {k: Output(type=references.get(v, None)) if isinstance(v, str) else Output(type=references.get(v['reference'], None)) for k, v in component['outputs'].items()}

  # Rest of component creation logic

  return new_component


def create_components_from_json(json_file):

  with open(json_file) as f:
    data = json.load(f)
  
  references = generate_references(data)

  resolved_json = replace_references(copy.deepcopy(data), references)

  components = [create_component_from_json(c, references) for c in resolved_json['components_framework'].values()]

  return components

# Usage:
json_file = "components.json"
components = create_components_from_json(json_file)