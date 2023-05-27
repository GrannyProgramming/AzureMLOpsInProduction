import sys
import ast
from workflowhelperfunc.workflowhelper import load_and_set_env_vars
from pathlib import Path

def main():
    print("Python path:", sys.path)

    file_path = sys.argv[1]
    var_list = ast.literal_eval(sys.argv[2])

    load_and_set_env_vars(file_path, var_list)

if __name__ == "__main__":
    main()
