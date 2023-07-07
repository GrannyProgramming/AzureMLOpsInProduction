import sys
import ast
from workflowhelperfunc.workflowhelper import load_and_set_env_vars, setup_logger, log_event


def main():
    """
    Load environment variables from a file and set them.
    The file path and optional variable list can be provided as command line arguments.

    Args:
        file_path (str): The path to the file containing environment variables.
        var_list (list, optional): List of specific variables to set. Defaults to None.
    """
    logger = setup_logger(__name__)

    try:
        if len(sys.argv) < 2:
            log_event(logger, 'error', "File path is not provided.")
            sys.exit(1)
        file_path = sys.argv[1]
        var_list = None

        if len(sys.argv) > 2:  # Check if var_list is provided
            var_list = ast.literal_eval(sys.argv[2])

        load_and_set_env_vars(file_path, var_list)
    except Exception as e:
        log_event(logger, 'error', f"An error occurred while loading and setting environment variables: {str(e)}")


if __name__ == "__main__":
    main()
