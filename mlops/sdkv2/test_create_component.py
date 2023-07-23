import unittest
import os
import yaml
from unittest.mock import patch, MagicMock
from create_component import create_component_from_yaml, create_components_from_yaml_file, compare_and_update_component
import glob

class TestCreateComponent(unittest.TestCase):

    def setUp(self):
        self.yaml_data = {}
        yaml_files = glob.glob('variables/dev/components/**/*.yaml', recursive=True)
        for yaml_file in yaml_files:
            with open(yaml_file, 'r') as f:
                yaml_data = yaml.safe_load(f)
                self.yaml_data.update(yaml_data['components'])

        self.component_datas = list(self.yaml_data.values())
        self.yaml_file = 'test.yaml'

    def tearDown(self):
        if os.path.exists(self.yaml_file):
            os.remove(self.yaml_file)

    def test_create_component_from_yaml(self):
        tag_value = 'test_tag'

        # Test successful case
        for component_data in self.component_datas:
            component_name = component_data['name']
            # Ensure that only 'integer' and 'number' types have default values in the inputs
            for input_name, input_data in component_data.get('inputs', {}).items():
                if input_data['type'] not in ['integer', 'number'] and 'default' in input_data:
                    input_data.pop('default')
            new_component = create_component_from_yaml(component_name, component_data, tag_value)
            # Add your checks here. Make sure to use component_data, not self.component_data

        # Test with missing inputs
        for component_name in self.yaml_data.keys():
            with self.assertRaises(KeyError):
                create_component_from_yaml(component_name, {}, tag_value)

    def test_create_components_from_yaml_file(self):
        with open(self.yaml_file, 'w') as f:
            f.write(yaml.dump({'components': self.yaml_data}))

        # Test successful case
        components = create_components_from_yaml_file(self.yaml_file)
        self.assertEqual(len(components), len(self.component_datas))
        # You may want to add more checks here

        # Test with file not found
        with self.assertRaises(FileNotFoundError):
            create_components_from_yaml_file('nonexistent.yaml')

    def test_create_component_from_yaml_incorrect_fields(self):
        component_data = {
            'name': 'test_component',
            'inputs': {
                'input1': {'type': 'string', 'optional': True, 'description': 'Test input 1'},
                'input2': {'type': 'integer', 'optional': True, 'description': 'Test input 2'}
            },
            'outputs': {'output1': {'type': 'string'}, 'output2': {'type': 'integer'}},
            'code': 'test_component.py',
            'environment': 'test_environment',
            'display_name': 'Test Component',
            'unexpected_field': 'unexpected_value'
        }
        with self.assertRaises(TypeError):
            create_component_from_yaml('test_component', component_data, 'test_tag')




    def test_create_component_from_yaml_invalid_input_type(self):
        with self.assertRaises(AttributeError):
            create_component_from_yaml('test_component', 'invalid_input', 'test_tag')
            
    def test_create_component_from_yaml_empty_inputs(self):
        with self.assertRaises(KeyError):
            # Pass an empty dictionary
            create_component_from_yaml('test_component', {}, 'test_tag')

    def test_create_component_from_yaml_missing_fields(self):
        component_data = {
            'name': 'test_component',
            # Missing 'inputs'
            'outputs': {'output1': {'type': 'str'}, 'output2': {'type': 'int'}},
            'code': 'test_component.py',
            'environment': 'test_environment',
            'display_name': 'Test Component'
        }
        with self.assertRaises(KeyError):
            create_component_from_yaml('test_component', component_data, 'test_tag')

    def test_create_component_from_yaml_incorrect_fields(self):
        component_data = {
            'name': 'test_component',
            'inputs': {'input1': {'type': 'str', 'default': 'default_value'}, 'input2': {'type': 'int', 'default': 10}},
            'outputs': {'output1': {'type': 'str'}, 'output2': {'type': 'int'}},
            'code': 'test_component.py',
            'environment': 'test_environment',
            'display_name': 'Test Component',
            # Add an unexpected field
            'unexpected_field': 'unexpected_value'
        }
        with self.assertRaises(TypeError):
            # This should raise a TypeError because the create_component_from_yaml function does not expect the 'unexpected_field' key
            create_component_from_yaml('test_component', component_data, 'test_tag')

    @patch('create_component.initialize_mlclient')
    def test_compare_and_update_component(self, mock_initialize_mlclient):
        mock_client = MagicMock()
        mock_initialize_mlclient.return_value = mock_client

        for component_data in self.component_datas:
            mock_component = MagicMock()
            mock_component.name = component_data['name']
            # Add your mock component setup here. Make sure to use component_data, not self.component_data

            # Test component exists and is identical
            compare_and_update_component(mock_client, mock_component)
            mock_client.components.list.assert_called()
            mock_client.components.get.assert_called_once_with(name=mock_component.name, version=mock_component.latest_version)
            self.assertEqual(mock_component.component.call_count, 0)
            mock_client.components.list.reset_mock()

            # Test component exists and is different
            mock_component.command = 'python --input1 ${inputs.input1} --input2 ${inputs.input2} --output1 ${outputs.output1}'
            compare_and_update_component(mock_client, mock_component)
            mock_client.components.list.assert_called()
            mock_client.components.get.assert_called_with(name=mock_component.name, version=mock_component.latest_version)
            mock_client.create_or_update.assert_called_once_with(mock_component.component)
            mock_client.components.list.reset_mock()

            # Test component does not exist
            mock_client.components.list.return_value = []
            compare_and_update_component(mock_client, mock_component)
            mock_client.components.list.assert_called()
            mock_client.create_or_update.assert_called_with(mock_component.component)

            # Test with exception
            mock_client.components.list.side_effect = Exception('Test exception')
            with self.assertRaises(Exception):
                compare_and_update_component(mock_client, mock_component)

if __name__ == '__main__':
    unittest.main()
