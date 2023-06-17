FROM mcr.microsoft.com/azureml/openmpi4.1.0-ubuntu20.04
FROM python:3.9

# Install Python packages
# RUN pip install \
#     # pydata
#     numpy==1.21.2 \
#     scipy==1.7.1 \
#     pandas==1.3.0 \
#     scikit-learn==0.24.2 \
#     adlfs==2021.9.1 \
#     fsspec==2021.8.1 \
#     # trees
#     xgboost==1.4.2 \
#     lightgbm==3.2.1 \
#     # tracking
#     mlflow==1.20.2 \
#     azureml-mlflow==1.34.0 \
#     # visualization
#     matplotlib==3.4.3 \
#     # python tools
#     tqdm==4.62.2 \
#     joblib==1.0.1 \
#     jupyter==1.0.0 \
#     ipykernel==6.4.1 \
#     papermill==2.3.3

COPY requirements.txt .
RUN pip install -r requirements.txt && rm requirements.txt

# set command
CMD ["bash"]
