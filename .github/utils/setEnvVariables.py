import argparse
import json
import subprocess

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("file_path", help="path to JSON file containing environment variables")
    args = parser.parse_args()

    env_file = args.file_path
    with open(env_file) as f:
        env_vars = json.load(f)
    
    for key, value in env_vars.items():
        print(f"Setting environment variable {key.upper()}")
        subprocess.run(['export', f"{key.upper()}='{value}'"], shell=True)

if __name__ == "__main__":
    main()
