<!-- Place this tag in your head or just before your close body tag. -->
[![stars - ds-aml-mlops](https://img.shields.io/github/stars/grannyprogramming/ds-aml-mlops?style=social)](https://github.com/grannyprogramming/ds-aml-mlops)
[![forks - ds-aml-mlops](https://img.shields.io/github/forks/grannyprogramming/ds-aml-mlops?style=social)](https://github.com/grannyprogramming/ds-aml-mlops/fork)
[![GitHub tag](https://img.shields.io/github/tag/grannyprogramming/ds-aml-mlops?include_prereleases=&sort=semver&color=blue)](https://github.com/grannyprogramming/ds-aml-mlops/releases/)
[![License](https://img.shields.io/badge/License-MIT-blue)](#license)
[![issues - ds-aml-mlops](https://img.shields.io/github/issues/grannyprogramming/ds-aml-mlops)](https://github.com/grannyprogramming/ds-aml-mlops/issues)

# Table of Contents

1. [Introduction to Azure Machine Learning and MLOps](#introduction-to-azure-machine-learning-and-mlops)
   1. [What is MLOps?](#what-is-mlops)
   2. [Applying MLOps in Azure](#applying-mlops-in-azure)
2. [Components of MLOps](#components-of-mlops)
3. [Forking the Repository](#forking-the-repository)
4. [Quickstart Guide](#quickstart-guide)
   1. [What You'll Need](#what-youll-need)
   2. [Steps](#steps)
   3. [Help](#help)
5. [Running the GitHub Workflow](#running-the-github-workflow)
6. [Checking Workflow Status via UI](#checking-workflow-status-via-ui)
7. [Understanding the GitHub Actions Workflow](#understanding-the-github-actions-workflow)

# Introduction to Azure Machine Learning and MLOps

Azure Machine Learning is a comprehensive cloud-based machine learning service from Microsoft that offers capabilities for building, training, and deploying machine learning models. It simplifies the process of creating models by providing an easy-to-use interface and a wide range of tools and services.

## What is MLOps?

MLOps, or DevOps for Machine Learning, brings together the best practices from the fields of machine learning and software development to help teams collaboratively build, validate, deliver, and monitor ML models. It helps to increase efficiency, reduce errors, and streamline the deployment process.

## Applying MLOps in Azure 

With Azure Machine Learning, you can implement MLOps practices to automate and manage the lifecycle of your machine learning models. This includes the creation of reusable pipelines, automation of machine learning tasks, continuous integration and delivery (CI/CD) of models, model versioning, and monitoring of model performance.

# Components of MLOps

Here are some of the key components associated with MLOps in Azure:

1. **Data**: The raw material for any machine learning model. The quality and relevance of your data significantly impacts the model's performance.

2. **Model Training**: The process of teaching a model to make predictions by feeding it data. This usually involves selecting a suitable algorithm and tuning hyperparameters.

3. **Model Validation**: Checking the accuracy and reliability of the model by testing it on a separate set of data.

4. **Model Deployment**: Making the trained model available for use in a production environment.

5. **Automation**: Automating repetitive tasks to speed up the development process and reduce the chance of errors.

6. **Continuous Integration and Continuous Delivery (CI/CD)**: A set of practices that involve automatically building, testing, and deploying models to ensure they can be released to production at any time.

7. **Monitoring**: Continually checking the performance of models in production to detect any problems or changes in performance.

8. **Versioning**: Keeping track of different versions of models and data to ensure reproducibility and traceability.

9. **Infrastructure**: The hardware and software resources needed to run your machine learning workloads, which in the case of Azure Machine Learning, are provided as cloud services.

10. **Governance**: Policies and regulations that guide how machine learning models are developed and used, including data privacy and ethical considerations.

## 🍴 Forking the Repository

Before you start, you need a copy of the repository in your GitHub account. This process is known as "forking". Here's how to do it:

1. **Go to the Repository**: 🔎 Navigate to the main page of the repository on GitHub.

2. **Optionally - Star the Repository**: ⭐ Click on the "Star" button for easier reference in the future to this repo, this will navigate you to the top of this page where you can star/favourite this repositry

[![stars - ds-aml-mlops](https://img.shields.io/github/stars/grannyprogramming/ds-aml-mlops?style=social)](https://github.com/grannyprogramming/ds-aml-mlops)

3. **Fork the Repository**: 🍴 Click on the "Star" button for easier reference in the future to this repo (top right) and then "Fork" button at the top-right of the page. This will create a copy of the repository under your GitHub account.

[![forks - ds-aml-mlops](https://img.shields.io/github/forks/grannyprogramming/ds-aml-mlops?style=social)](https://github.com/grannyprogramming/ds-aml-mlops/fork)



4. **Clone the Repository**: 💻 Now, you need a local copy of the repository on your computer. Open your terminal (or PowerShell), navigate to the directory where you want to clone the repository, and run the following command:

    ```bash
    git clone https://github.com/YOUR_USERNAME/REPO_NAME.git
    ```

    Make sure to replace `YOUR_USERNAME` with your GitHub username, and `REPO_NAME` with the name of the repository. 

5. **Navigate to the Repository Directory**: 🗺️ Once the repository is cloned, use the `cd` command to navigate into it:

    ```bash
    cd REPO_NAME
    ```

    Replace `REPO_NAME` with the name of the repository.

Now you're ready to run the `quickstart.ps1` script! 🚀 Remember, you'll need to pass the path to your JSON configuration file as an argument. 

# 🚀 Quickstart Guide 

Welcome to the **Quickstart Guide**! 🎉 This document will assist you step by step to run the `quickstart.ps1` script. This incredible script helps in setting up various environments for your project using a provided JSON configuration file. 

## 📝 What You'll Need

- **PowerShell**: 💻 The command-line shell used to run the script. Pre-installed on most Windows machines, and available for [Mac](https://docs.microsoft.com/en-us/powershell/scripting/install/installing-powershell-core-on-macos?view=powershell-7.1) and [Linux](https://docs.microsoft.com/en-us/powershell/scripting/install/installing-powershell-core-on-linux?view=powershell-7.1).

- **GitHub CLI**: Octocat's powerful tool, [GitHub CLI](https://cli.github.com/), is needed for this script. Make sure you have it installed on your machine.

- **Azure CLI**: ☁️ Your gateway to Azure, the [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli), needs to be ready on your machine.

- **JSON Configuration File**: 🗂️ A JSON file that specifies the configurations for different environments (dev, test, prod). This guide assumes that you already have this file.

## 🚦 Steps

1. **Open PowerShell**: 🔍 Search for "PowerShell" in your computer's Start Menu (Windows) or Applications Folder (Mac), and click to open it.

2. **Navigate to the Script**: 🗺️ Use the `cd` command to navigate to the directory containing your `quickstart.ps1` script. If your script is in a folder named "scripts" on your desktop, you'd type `cd Desktop/scripts`.

3. **Run the Script**: 🏃‍♀️ Type `.\quickstart.ps1 <PathToYourJsonFile>` to run the script. Replace `<PathToYourJsonFile>` with the path to your JSON file. If your JSON file is in the same "scripts" folder, you'd type `.\quickstart.ps1 my_config.json`.

    This magic script will:

    - Authenticate with GitHub
    - Extract the configuration details from your JSON file for each environment
    - Log in to Azure and set up the corresponding service principal for each environment
    - Gracefully update GitHub with the details for each environment

4. **Follow the Prompts**: 📢 The script will guide you through the rest of the process. It might ask for your GitHub credentials (if you haven't logged in before) or ask to create a service principal in Azure.

## ⚠️ Help

If you encounter any issues, please check:

- ✔️ The path to your JSON file is correct.
- ✔️ You've installed all necessary tools (PowerShell, GitHub CLI, Azure CLI).
- ✔️ Your internet connection, as the script requires access to GitHub and Azure.

## 🚀 Running the GitHub Workflow

After setting up the service principal and GitHub secrets, you're ready to kick off the GitHub workflow. This workflow should be set up for manual triggering using `workflow_dispatch`. 

Here's how to do it using the GitHub CLI:

1. **List All Workflows**: 👀 First, list all workflows available in your repository. In your terminal or PowerShell, type the following command:

    ```bash
    gh workflow list
    ```

    This will display a list of all workflows in your repository.

2. **Run the Workflow**: 🏃‍♀️ Once you've identified the workflow you want to run, in our case the workflow will be called "task_aml_mlops_e2e" you can dispatch it using the following command:

    ```bash
    gh workflow run WORKFLOW_NAME.yml
    ```

    Replace `WORKFLOW_NAME.yml` with the actual filename of your workflow i.e., "task_aml_mlops_e2e".

3. **Check Workflow Status**: 📊 To check the status of your workflow, use:

    ```bash
    gh run list
    ```

    This command will list all recent workflow runs, along with their status (completed, in-progress, failed, etc.)

## 🖥️ Checking Workflow Status via UI

If you prefer to visually check the status of your workflows, GitHub's user interface provides a detailed view of each workflow run. Here's how to access it:

1. **Go to Your Repository**: 🔍 Navigate to the main page of your repository on GitHub.

2. **Access Actions Tab**: 🎬 Click on the "Actions" tab at the top of the repository page. This tab provides an overview of all workflow runs associated with your repository.

    ![Actions Tab](https://docs.github.com/assets/images/help/repository/repo-tabs-actions.png)

3. **View Workflow Runs**: 👀 Here, you'll see a list of all runs for all workflows in your repository, with the most recent runs listed first. You can click on the name of a run to view more detailed information.

4. **Check Run Details**: 🕵️‍♀️ Once you click on a specific run, you'll see a summary at the top of the page, and a detailed log of the run at the bottom. If the run is still in progress, you can watch the logs update in real-time.

That's it! You've successfully navigated to and viewed your workflow runs on GitHub. You can return to this page at any time to view the status of a run, or to troubleshoot if something goes wrong.

That's it! Your GitHub workflow should now be running. Once it's completed, you can check the logs for any output or errors.

🔧 Remember, GitHub workflows are highly customizable. Always check the `.github/workflows` directory in your repository to understand what your workflows are doing and what inputs they might require.

## 🚀 Understanding the GitHub Actions Workflow

Your GitHub Actions Workflow, named `Azure ML Workflow`, is triggered whenever a push event is made to the `main` branch. It consists of several jobs, each with individual tasks or "steps".

1. **Checkout Code**: Utilizes the `actions/checkout@v3` action to clone the repository into the GitHub runner. This makes your entire codebase available for subsequent steps in the workflow.

2. **Set Up Python 3.9**: Leverages the `actions/setup-python@v4` action to set up a specific Python version (3.9) in the runner's environment. This ensures that all subsequent steps using Python are executed with the correct Python version.

3. **Install Dependencies**: Executes a Python script (`install_dependencies.py`) that manages the installation of necessary Python packages and dependencies required for the rest of the workflow.

4. **Build Wheel And Install Helper Functions**: This step includes two tasks. First, it changes the current directory to where the Python wheel configurations are (`py_wheels`), then runs `setup.py` to build a wheel distribution of helper functions. Finally, it installs the generated wheel files, making these functions available for import in other scripts.

5. **Json Schema Validation**: Executes a Python script (`json_schema_validator.py`) to validate the structure of your JSON configuration files. This is crucial for ensuring data integrity and error prevention.

6. **Set Env Variables**: Executes a Python script (`set_env_variables.py`) that sets environment variables for the runner based on parameters specified in a JSON file. This allows these variables to be used in subsequent steps.

7. **Azure Login**: This step authenticates with Azure using service principal credentials stored as GitHub secrets. This authenticated session is used for deploying resources and managing services within Azure in subsequent steps.

8. **Compile & Deploy Bicep Templates**: Compiles your Bicep infrastructure-as-code templates into ARM templates using the `bicep build` command. It then runs a Python script (`create_azure_resources.py`) to deploy these templates to Azure, effectively setting up your required cloud resources.

9. **Create AML Instance/Clusters**: Executes a Python script (`create_compute.py`) to set up an Azure Machine Learning workspace and create associated compute clusters within it.

10. **Create An MLtable**: Executes a Python script (`createMlTable.py`) to create a table in your Azure Machine Learning workspace, serving as a place to store and manage your ML data.

11. **Create Data Assets**: Executes a Python script (`create_data_asset.py`) that creates data assets in Azure Machine Learning based on a provided JSON file. Data assets can include datasets, datastores, and more.

12. **Create AML Environments**: Executes a Python script (`create_environments.py`) to create multiple Azure Machine Learning environments. These environments contain the Python packages, environment variables, and software settings necessary for running machine learning experiments and models.

13. **Create Components**: Executes a Python script (`create_component.py`) that creates components in Azure Machine Learning from a provided JSON file. These components can include training scripts, scoring scripts, and other reusable pieces of your ML workflows.

14. **Create Pipelines**: Executes a Python script (`create_pipeline.py`) to create pipelines in Azure Machine Learning from a provided JSON file. These pipelines define the steps and sequence of your machine learning workflows.

15. **Create action groups**: Executes a Python script (`create_action_groups.py`) that creates action groups in Azure Monitor. Action groups are collections of notification preferences defined by the user.

16. **Create alert processing rules based on severity**: Executes a Python script (`alert_processing_rules.py`) that creates alert processing rules in Azure Monitor. These rules allow you to automate the response to alerts based on their severity.

17. **Create AML Alerts**: Executes a Python script (`create_alerts.py`) to create alert rules in Azure Monitor from a provided JSON file. These rules help you monitor the status of your resources, services, and potential security threats.

Each step in this workflow plays a crucial role in ensuring a successful execution of your MLOps pipeline. From setting up the correct environment and installing dependencies, to deploying resources in Azure, and even setting up alerts to monitor your resources - everything is automated and visible through GitHub Actions.



## License

Released under [MIT](/LICENSE) by [@grannyprogramming](https://github.com/grannyprogramming).