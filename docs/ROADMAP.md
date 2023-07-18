# Roadmap

There are three main milestones we believe will greatly increase Azure MLOps  reliability and capability:
- [ ] Achieve a flexible and simple baseline. 
- [ ] Incorporate preview features from AML
- [ ] Create modular templates that can be inserted to the baseline

## Our current focus:

- [x] **Achieve a flexible and simple baseline. 🎉**
  - [x] Setting up a wheel file for the gh workflow 
  - [x] Creating AML Computes 
    - [x] Extending this by checking compute exists and differentiating between viable computes.
    - [x] Adding in logic for AKS or/and Kubernetes [#10](https://github.com/GrannyProgramming/AzureMLOpsInProduction/issues/10)
  - [x] Creating AML Environments
    - [x] Scalable script to take one config file and create multipile environments
    - [x] Extend to create environments for Conda, Docker and Docker Build [#12](https://github.com/GrannyProgramming/AzureMLOpsInProduction/issues/12)
    - [x] Check AML pre-existing environment against the JSON config [#11](https://github.com/GrannyProgramming/AzureMLOpsInProduction/issues/11)
  - [x] Creating AML Data Assets
    - [x] Scalable script that identifies multiples data asset types and registers them
    - [ ] Optional step to create data as mltable, csv etc.,   
  - [x] Creating AML Components
    - [x] Scalable JSON that will reduce repition and follow DRY principles
    - [x] Scalable custom python file that can parse and validate this JSON
    - [ ] Check pre-existing component configuration beofer creating/updating
  - [x] Creating AML Pipelines
    - [x] Scalable pipeline using predefined components 
    - [x] Defining pipelines within pipelines to add an extra layer of seperation i.e., data pipeline, train pipeline and evaluate pipeline 
    - [] Parralell pipelines
  - [ ] Creating AML Deployment
    - [ ] Scalable endpoints creation based on the users config file, should take into account all options.
  - [ ] Enabling Automatic Retraining 
    - [ ] Incorporating Azure Data Drift 
  - [x] Enabling Monitoring & Testing
    - [x] Setting Up Action Groups
      - [ ] Providing relevant documentation to enable User configuration
    - [x] Setting Up Action Rules
      - [ ] Providing relevant documentation to enable User configuration
    - [x] Setting Up Alert Rules 
      - [x] Providing relevant example Kusto logic for Relevant Alerts  
      - [ ] Providing relevant documentation to enable User configuration
    - [ ] Setting Up Azure Dashboard
       - [ ] Providing relevant example Kusto logic for Relevant Tracking 


- [ ] **Incorporate preview features from AML**
  - [ ] AML Shared Registry
  - [ ] AML Data Drift 
  - [ ] AML Model Monitoring
  - [ ] AML Feature Tables#

- [ ] **Modular Templates**
  - [ ] Using MLOps in Deep Learning - Deepspeed, Ray distributon, Pytorch etc.,
    - [ ] Using MLOps With Parralell Models
  - [ ] Using MLOps With OpenAI
  - [ ] Using MLOps With Sweep Parameters 
  - [ ] Implementing different Model Deployment Patterns 
 
- [ ] **Improve existing Baseline**
  - [ ] CLIv2 Approach 
  - [ ] Azure DevOps 
  - [ ] Terraform Infra
  - [ ] Adding security, netwroking etc
  - [ ] Additional testing i.e., Smoke Testing
  
## Codebase improvements
By improving the codebase and developer ergonomics, we accelerate progress. Some examples:
- [ ] Refactor Code: Restructure code for improved understandability and efficiency.
- [ ] Adopt Design Patterns: Use standard solutions for common design problems to speed up development.
- [ ] Write Tests: Implement unit, integration, and end-to-end tests to catch bugs early and prevent regressions.
- [ ] Improve Documentation: Enhance documentation clarity and update for smoother understanding.
- [ ] Optimize Build Processes: Improve the speed and reliability of build and deployment processes.
- [ ] Conduct Code Reviews: Maintain code quality and catch potential issues early.
- [ ] Adopt New Technologies: Utilize updated tools, libraries, or frameworks to enhance development speed.
- [ ] Automate Repetitive Tasks: Automate frequent tasks to reduce time and effort.
- [ ] Improve Code Consistency: Use tools like linters and formatters and agree on coding standards for readable code.

# How you can help out
To get started, please refer to our contribution guide, which outlines the process for submitting pull requests. Remember, the best way to learn is to get your hands dirty, so don't be afraid to try something new or ask questions. We appreciate all contributions and are always happy to help guide you.

You can:
- Outreach and Education: Write about our project, create tutorials or how-to guides, or even organize webinars or meetups to introduce others to our project.
Code Reviews: Code review is a great way to share knowledge, maintain code quality and find bugs or improvements.
- Trainings: If you are well-versed in a certain technology, framework, or principle that we are using or planning to use, consider conducting training sessions.
- Project Management: Help us manage the project, keep track of open issues, prioritize them, and ensure they are assigned and closed in a timely manner.Contribute to Code: Help us with our open issues, or suggest new enhancements. Your expertise can help make our codebase more robust and efficient.
- Testing: Aid us in testing the existing and upcoming features. You can report bugs, suggest improvements, and even create automated testing scripts.
- Documentation: If you enjoy writing and explaining complex ideas in a simple way, help us improve our documentation. Good documentation makes the project more accessible and maintainable.

Volunteer work in any of these will get acknowledged.