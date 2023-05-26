from setuptools import setup

setup(
    name='workflowHelperFunc',
    version='1.0.1',
    author='amcg809',
    author_email='amcg809@gmail.com',
    description='A helper function for the workflow (Logging, setEnvVariables, etc.))',
    py_modules=['loggingConfig'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.9',
)
