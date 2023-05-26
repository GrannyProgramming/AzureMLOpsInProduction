import sys
from workflowHelperFunc.workflowHelper import load_and_set_env_vars
from pathlib import Path

def main():
    print("Python path:", sys.path)
    # The first argument (sys.argv[1]) is the command line argument
    vars_or_path = sys.argv[1]

    # Check if the argument is a file path or a list of variables
    if Path(vars_or_path).exists():
        # If it's a file path, pass it as the 'file_path' parameter
        load_and_set_env_vars(file_path=vars_or_path)
    else:
        # If it's not a file path, split the string into a list of variables
        var_list = vars_or_path.split()
        load_and_set_env_vars(var_list=var_list)

if __name__ == "__main__":
    main()
