# https://learn.microsoft.com/en-us/azure/machine-learning/how-to-create-component-pipeline-python?view=azureml-api-2#define-component-using-python-function
# mldesigner package contains the command_component which can be used to define component from a python function
# Import the prep function from prep.py
from dataScience.src.prep import prep
from mldesigner import command_component, Input, Output
# Prep component
@command_component(
    name="prep",
    display_name="Prep Component",
    description="Tidy data",
    environment="azureml:pydata-example:2",
)
def prep_component(
    raw_data: Input(type="mltable"),
    prep_data: Output(type="mltable"),
):
    # Call the prep function from the imported prep module
    prep(raw_data, prep_data)