# 1. Import the required libraries
import json
import yaml
import logging
import sys
#import required libraries for environments examples
from azure.ai.ml.entities import Environment, BuildContext
from workflowhelperfunc.workflowhelper import initialize_mlclient

# 2. Configure workspace details and get a handle to the workspace
ml_client = initialize_mlclient()

# Set up logging
logging.basicConfig(level=logging.INFO)

# #Create an environment from a Docker build context
env_docker_context = Environment(
    build=BuildContext(path="variables/dev/environments/dockerContexts/exDockerEnv"),
    name="docker-build-example",
    description="Environment created from a Build Docker context.",
)
ml_client.environments.create_or_update(env_docker_context)
