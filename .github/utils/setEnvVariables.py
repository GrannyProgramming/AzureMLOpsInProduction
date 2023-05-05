import argparse
import json
import os
from pathlib import Path

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("file_path", help="path to JSON file containing environment variables")
    args = parser.parse_args()

    env_file = Path(args.file_path)
    with env_file.open() as f:
        env_vars = json.load(f)
    for key, value in env_vars.items():
        print(f"Setting environment variable {key}")
        print(f"Value: {value}")
        os.environ[key] = value

if __name__ == "__main__":
    main()
