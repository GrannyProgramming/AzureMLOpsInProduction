<!-- Place this tag in your head or just before your close body tag. -->
_Social buttons_

[![stars - ds-aml-mlops](https://img.shields.io/github/stars/grannyprogramming/ds-aml-mlops?style=social)](https://github.com/grannyprogramming/ds-aml-mlops)
[![forks - ds-aml-mlops](https://img.shields.io/github/forks/grannyprogramming/ds-aml-mlops?style=social)](https://github.com/grannyprogramming/ds-aml-mlops/fork)

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

2. **Fork the Repository**: 🍴 Click on the "Star" button for easier reference in the future to this repo (top right) and then "Fork" button at the top-right of the page. This will create a copy of the repository under your GitHub account.

[![stars - ds-aml-mlops](https://img.shields.io/github/stars/grannyprogramming/ds-aml-mlops?style=social)](https://github.com/grannyprogramming/ds-aml-mlops)
[![forks - ds-aml-mlops](https://img.shields.io/github/forks/grannyprogramming/ds-aml-mlops?style=social)](https://github.com/grannyprogramming/ds-aml-mlops/fork)



3. **Clone the Repository**: 💻 Now, you need a local copy of the repository on your computer. Open your terminal (or PowerShell), navigate to the directory where you want to clone the repository, and run the following command:

    ```bash
    git clone https://github.com/YOUR_USERNAME/REPO_NAME.git
    ```

    Make sure to replace `YOUR_USERNAME` with your GitHub username, and `REPO_NAME` with the name of the repository. 

4. **Navigate to the Repository Directory**: 🗺️ Once the repository is cloned, use the `cd` command to navigate into it:

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

