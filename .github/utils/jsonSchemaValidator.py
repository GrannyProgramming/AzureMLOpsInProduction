import os
import sys
import json
from jsonschema import validate, ValidationError

class SchemaValidator:
    """A class to validate JSON files against their schema files within a directory."""

    def __init__(self, root_dir):
        """Initialize SchemaValidator with the root directory."""
        self.root_dir = root_dir

    def gather_json_files(self):
        """
        Traverse the root directory and gather all JSON files.
        Return a list of tuples (directory path, json file name).
        """
        json_files = []

        for dir_path, dirs, files in os.walk(self.root_dir):
            for file in files:
                if file.endswith('.json') and file != "parameters.json":
                    json_files.append((dir_path, file))
        return json_files

    def get_schema_path(self, dir_path, json_file):
        """
        Derive the schema path from the json file path.
        """
        # Split the directory path into components
        dir_components = dir_path.split(os.sep)

        # Replace the first directory with 'json-schema'
        try:
            dir_components[1] = 'json-schema'
        except IndexError:
            print(f"Error: The path '{dir_path}' does not have the expected structure. Skipping this path.")
            return None

        # Get the base name of the JSON file and remove the '.json' extension
        schema_file_name = os.path.splitext(json_file)[0] + 'Schema.json'

        # Reconstruct the schema file path
        schema_path = os.path.join(*dir_components, schema_file_name)

        # Check if schema file exists
        if not os.path.isfile(schema_path):
            print(f"Error: Schema file '{schema_path}' does not exist. Skipping this path.")
            return None

        return schema_path

    @staticmethod
    def validate_json_with_schema(json_filepath, schema_filepath):
        """
        Validate a single JSON file against its schema.
        Print success or error message.
        """
        with open(json_filepath) as jf, open(schema_filepath) as sf:
            try:
                data = json.load(jf)
                schema = json.load(sf)
                validate(instance=data, schema=schema)
                print(f"{os.path.basename(json_filepath)} has been successfully validated against {os.path.basename(schema_filepath)}")
            except ValidationError as e:
                print(f"Validation failed for {os.path.basename(json_filepath)}. Schema: {os.path.basename(schema_filepath)}")
                print(f"Error details: {str(e)}")

    def execute(self):
        """
        Main method to gather JSON files, then validate JSON against its schema.
        """
        json_files = self.gather_json_files()

        for dir_path, json_file in json_files:
            json_filepath = os.path.join(dir_path, json_file)
            schema_filepath = self.get_schema_path(dir_path, json_file)
            if schema_filepath is not None:
                self.validate_json_with_schema(json_filepath, schema_filepath)

if __name__ == "__main__":
    """Main execution of the script: Initialize the SchemaValidator and execute it."""
    # Get the root directory from command line arguments
    root_dir = sys.argv[1]
    validator = SchemaValidator(root_dir)
    validator.execute()
