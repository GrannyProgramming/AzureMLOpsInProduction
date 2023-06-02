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
                if file.endswith('.json'):
                    json_files.append((dir_path, file))
        return json_files

    def get_schema_path(self, dir_path, json_file):
        """
        Derive the schema path from the json file path.
        """
        # Get the relative directory path from the root directory to the JSON file directory
        relative_dir_path = os.path.relpath(dir_path, self.root_dir)

        # Split the relative directory path into a list of directories
        dir_list = relative_dir_path.split(os.sep)

        # Check if the path has at least two levels
        if len(dir_list) < 2:
            print(f"Error: The path '{dir_path}' does not have the expected structure. Skipping this path.")
            return None

        # Replace the second directory (environment) with 'json-schema'
        dir_list[1] = 'json-schema'

        # Construct the schema directory path
        schema_dir_path = os.sep.join(dir_list)

        # Construct the schema file path
        schema_file = json_file.replace('.json', 'Schema.json')
        schema_path = os.path.join(self.root_dir, schema_dir_path, schema_file)

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
