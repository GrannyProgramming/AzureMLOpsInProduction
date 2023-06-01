// Creates a machine learning workspace, private endpoints and compute resources
// Compute resources include a GPU cluster, CPU cluster, compute instance and attached private AKS cluster

@description('Azure region of the deployment')
param location string

@description('Tags to add to the resources')
param tags object

@description('Resource ID of the application insights resource')
param applicationInsightsId string

@description('Resource ID of the container registry resource')
param containerRegistryId string

@description('Resource ID of the key vault resource')
param keyVaultId string

@description('Resource ID of the storage account resource')
param storageAccountId string

@description('Resource ID of the log analytic workspace resource')
// param logAnalyticsWorkspaceId string

param prefix string 
var uniqueSuffix = substring(uniqueString(resourceGroup().id), 0, 4)

@description('Machine learning workspace name')
var machineLearningName = '${prefix}-${uniqueSuffix}'


resource machineLearning 'Microsoft.MachineLearningServices/workspaces@2022-05-01' = {
  name: machineLearningName
  location: location
  tags: tags
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    // dependent resources
    applicationInsights: applicationInsightsId
    containerRegistry: containerRegistryId
    keyVault: keyVaultId
    storageAccount: storageAccountId
  }
}

output machineLearningId string = machineLearning.id
output machineLearningName string = machineLearning.name
