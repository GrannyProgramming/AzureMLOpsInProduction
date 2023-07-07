import os
import sys
import json
from jsonschema import validate, ValidationError
from workflowhelperfunc.workflowhelper import setup_logger, log_event


class SchemaValidator:
    """A class to validate JSON files against their schema files within a directory."""

    def __init__(self, root_dir, logger):
        """
        Initialize SchemaValidator with the root directory and logger.

        Args:
            root_dir (str): The root directory to traverse and validate JSON files.
            logger (logging.Logger): The logger object.
        """
        self.root_dir = root_dir
        self.logger = logger

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

        Args:
            dir_path (str): The directory path.
            json_file (str): The JSON file name.

        Returns:
            str: The schema file path.
        """
        # Split the directory path into components
        dir_components = dir_path.split(os.sep)

        # Replace the first directory with 'json-schema'
        try:
            dir_components[1] = 'json_schema'
        except IndexError:
            log_event(self.logger, 'error', f"The path '{dir_path}' does not have the expected structure. Skipping this path.")
            return None

        # Get the base name of the JSON file and remove the '.json' extension
        schema_file_name = os.path.splitext(json_file)[0] + '_schema.json'

        # Reconstruct the schema file path
        schema_path = os.path.join(*dir_components, schema_file_name)

        # Check if schema file exists
        if not os.path.isfile(schema_path):
            log_event(self.logger, 'error', f"Schema file '{schema_path}' does not exist. Skipping this path.")
            return None

        return schema_path

    def validate_json_with_schema(self, json_filepath, schema_filepath):
        """
        Validate a single JSON file against its schema.

        Args:
            json_filepath (str): The JSON file path.
            schema_filepath (str): The schema file path.
        """
        with open(json_filepath) as jf, open(schema_filepath) as sf:
            data = json.load(jf)
            schema = json.load(sf)

            try:
                validate(instance=data, schema=schema)
                log_event(self.logger, 'info', f"{os.path.basename(json_filepath)} has been successfully validated against {os.path.basename(schema_filepath)}")
            except ValidationError as e:
                log_event(self.logger, 'error', f"Validation failed for {os.path.basename(json_filepath)}. Schema: {os.path.basename(schema_filepath)}")
                log_event(self.logger, 'error', f"Error details: {str(e)}")
                raise SystemExit(e)

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
    logger = setup_logger(__name__)
    try:
        # Get the root directory from command line arguments
        if len(sys.argv) < 2:
            log_event(logger, 'error', "Root directory is not provided.")
            sys.exit(1)
        root_dir = sys.argv[1]

        validator = SchemaValidator(root_dir, logger)  # Pass the logger to SchemaValidator
        validator.execute()
    except Exception as e:
        log_event(logger, 'error', f"An error occurred during schema validation: {str(e)}")
