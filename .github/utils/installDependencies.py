'''
This code installs various dependencies and the Github CLI

'''

import subprocess

def install_dependencies():
    subprocess.run(['pip3', 'install', '--upgrade', 'pip'])
    subprocess.run(['pip', 'install', 'jsonschema'])
    # subprocess.run(['pip3', 'install', 'yq']) 
    # subprocess.run(['pip3', 'install', 'wheel'])
    # subprocess.run(['pip3', 'install', 'azure-cli', '--upgrade'])
    # subprocess.run(['pip3', 'install', 'azure-ai-ml'] )
    subprocess.run(['pip3', 'install', 'mltable'])
    # subprocess.run(['pip3', 'install', 'requests'])   
    subprocess.run(['pip3', 'install', 'pandas'])
    subprocess.run(['pip3', 'install', 'azureml-dataprep[pandas]'])
    # if subprocess.run(['which', 'bicep']).returncode != 0:
    #     subprocess.run(['curl', '-Lo', '/usr/local/bin/bicep', 'https://github.com/Azure/bicep/releases/latest/download/bicep-linux-x64'])
    #     subprocess.run(['chmod', '+x', '/usr/local/bin/bicep'])
    # if subprocess.run(['which', 'curl']).returncode != 0:
    #     subprocess.run(['sudo', 'apt', 'update'])
    #     subprocess.run(['sudo', 'apt', 'install', 'curl', '-y'])
    # subprocess.run(['curl', '-fsSL', 'https://cli.github.com/packages/githubcli-archive-keyring.gpg'], stdout=subprocess.PIPE)
    # curl_process = subprocess.run(['curl', '-fsSL', 'https://cli.github.com/packages/githubcli-archive-keyring.gpg'], stdout=subprocess.PIPE)
    # subprocess.run(['sudo', 'dd', 'of=/usr/share/keyrings/githubcli-archive-keyring.gpg'], input=curl_process.stdout)
    # subprocess.run(['sudo', 'chmod', 'go+r', '/usr/share/keyrings/githubcli-archive-keyring.gpg'])
    # subprocess.run(['echo', f"deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main"], stdout=subprocess.PIPE, shell=True)
    # subprocess.run(['sudo', 'tee', '/etc/apt/sources.list.d/github-cli.list'], stdin=subprocess.PIPE)
    # subprocess.run(['sudo', 'apt', 'update'])
    # subprocess.run(['sudo', 'apt', 'install', 'gh', '-y'])


install_dependencies()