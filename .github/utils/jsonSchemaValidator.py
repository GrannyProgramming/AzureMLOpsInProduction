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

    def get_schema_path(self, json_filepath):
        """
        Derive the schema path from the json file path.
        """
        # Assume the json file is in a directory equivalent to ${ matrix.environment }
        matrix_environment = os.path.basename(os.path.dirname(json_filepath))

        # Construct the schema path
        schema_path = os.path.join("variables", matrix_environment, "json-schema", "compute", "computeSchema.json")

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

        for json_filepath in json_files:
            schema_filepath = self.get_schema_path(json_filepath)
            self.validate_json_with_schema(json_filepath, schema_filepath)


if __name__ == "__main__":
    """Main execution of the script: Initialize the SchemaValidator and execute it."""
    # Get the root directory from command line arguments
    root_dir = sys.argv[1]
    validator = SchemaValidator(root_dir)
    validator.execute()
