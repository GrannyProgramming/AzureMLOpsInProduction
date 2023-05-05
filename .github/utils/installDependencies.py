import subprocess

def install_dependencies():
    subprocess.run(['pip3', 'install', '--upgrade', 'pip'])
    subprocess.run(['pip3', 'install', 'yq'])
    subprocess.run(['pip3', 'install', 'azure-cli', '--upgrade'])
    subprocess.run(['az', 'extension', 'add', '-n', 'azure-cli-ml'])
    subprocess.run(['az', 'extension', 'add', '-n', 'azureml-ai-ml'])
    subprocess.run(['pip3', 'install', 'azure-cli-ml', '--upgrade'])
    subprocess.run(['pip3', 'install', 'azure-ai-ml'])
    subprocess.run(['pip3', 'install', 'mltable'])
    if subprocess.run(['type', '-p', 'curl']).returncode != 0:
        subprocess.run(['sudo', 'apt', 'update'])
        subprocess.run(['sudo', 'apt', 'install', 'curl', '-y'])
    subprocess.run(['curl', '-fsSL', 'https://cli.github.com/packages/githubcli-archive-keyring.gpg'], stdout=subprocess.PIPE)
    subprocess.run(['sudo', 'dd', 'of=/usr/share/keyrings/githubcli-archive-keyring.gpg'], stdin=subprocess.PIPE, input=subprocess.stdout)
    subprocess.run(['sudo', 'chmod', 'go+r', '/usr/share/keyrings/githubcli-archive-keyring.gpg'])
    subprocess.run(['echo', f"deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main"], stdout=subprocess.PIPE)
    subprocess.run(['sudo', 'tee', '/etc/apt/sources.list.d/github-cli.list'], stdin=subprocess.PIPE, input=subprocess.stdout)
    subprocess.run(['sudo', 'apt', 'update'])
    subprocess.run(['sudo', 'apt', 'install', 'gh', '-y'])

install_dependencies()