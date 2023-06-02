import os
import sys
import json
import logging
from jsonschema import validate, ValidationError
from workflowhelperfunc.workflowhelper import log_event, setup_logger


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

    # ... rest of the class code ...


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
