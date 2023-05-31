import os
import sys
import json
from jsonschema import validate, ValidationError
from collections import defaultdict

class SchemaValidator:
    """A class to validate JSON files against their schema files within a directory."""

    def __init__(self, root_dir):
        """Initialize SchemaValidator with the root directory."""
        self.root_dir = root_dir

    def gather_json_schema_pairs(self):
        """
        Traverse the root directory, check, and pair JSON and Schema files.
        Return a dictionary of JSON and Schema file pairs.
        """
        json_schema_dict = defaultdict(dict)

        for dir_path, dirs, files in os.walk(self.root_dir):
            for file in files:
                if file.endswith('.json') and 'Schema' not in file:
                    schema_file = file.replace('.json', 'Schema.json')
                    if schema_file in files:
                        json_schema_dict[dir_path][file] = schema_file
        return json_schema_dict

    @staticmethod
    def validate_json_with_schema(dir_path, json_file, schema_file):
        """
        Validate a single JSON file against its schema.
        Print success or error message.
        """
        with open(os.path.join(dir_path, json_file)) as jf, \
                open(os.path.join(dir_path, schema_file)) as sf:
            try:
                data = json.load(jf)
                schema = json.load(sf)
                validate(instance=data, schema=schema)
                print(f"{json_file} has been successfully validated against {schema_file}")
            except ValidationError as e:
                print(f"Validation failed for {json_file} against {schema_file}")
                print(f"Error details: {str(e)}")

    def execute(self):
        """
        Main method to gather JSON and Schema pairs, then validate JSON against its schema.
        """
        json_schema_dict = self.gather_json_schema_pairs()

        for dir_path, file_pairs in json_schema_dict.items():
            for json_file, schema_file in file_pairs.items():
                self.validate_json_with_schema(dir_path, json_file, schema_file)


if __name__ == "__main__":
    """Main execution of the script: Initialize the SchemaValidator and execute it."""
    # Get the root directory from command line arguments
    root_dir = sys.argv[1]
    validator = SchemaValidator(root_dir)
    validator.execute()
