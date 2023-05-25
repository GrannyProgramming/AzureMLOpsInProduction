// Import the required modules
targetScope = 'subscription'

param resourceGroupName string
param location string
param logAnalyticsWorkspaceName string
param logAnalyticsResourceGroupName string


@minLength(2)
@maxLength(10)
@description('Prefix for all resource names.')
param prefix string

@description('Set of tags to apply to all resources.')
param tags object = {}

var name = toLower('${prefix}')

// Dependent resources for the Azure Machine Learning workspace
resource azResourceGroup 'Microsoft.Resources/resourceGroups@2021-04-01' = {
  dependsOn: []
  name: resourceGroupName
  location: location
}

module keyvault 'modules/keyVault.bicep' = {
  name: 'kv-${name}-deployment'
  dependsOn: [
    azResourceGroup
  ]
  scope: resourceGroup(resourceGroupName)
  params: {
    location: location
    keyvaultName: 'kv-${name}'
    tags: tags
  }
}

module storage 'modules/storageAccount.bicep' = {
  name: 'st${name}-deployment'
  dependsOn: [
    azResourceGroup
  ]
  scope: resourceGroup(resourceGroupName)
  params: {
    location: location
    storageName: 'st${name}'
    storageSkuName: 'Standard_LRS'
    tags: tags
  }
}

module containerRegistry 'modules/containerRegistry.bicep' = {
  name: 'cr${name}-deployment'
  dependsOn: [
    azResourceGroup
  ]
  scope: resourceGroup(resourceGroupName)
  params: {
    location: location
    prefix: 'cr${name}'
    tags: tags
  }
}

module applicationInsights 'modules/applicationInsights.bicep' = {
  name: 'appi-${name}-deployment'
  dependsOn: [
    azResourceGroup
  ]
  scope: resourceGroup(resourceGroupName)
  params: {
    location: location
    prefix: 'appi-${name}'
    tags: tags
  }
}

module amlWorkspace './modules/amlWorkspace.bicep' = {
  name: 'mlw-${name}-deployment'
  scope: resourceGroup(resourceGroupName)
  params: {
    // workspace organization
    prefix: 'mlw-${name}'
    location: location
    tags: tags

    // dependent resources
    // logAnalyticsWorkspaceId: logAnalytics.outputs.logAnalyticsWorkspaceId
    applicationInsightsId: applicationInsights.outputs.applicationInsightsId
    containerRegistryId: containerRegistry.outputs.containerRegistryId
    keyVaultId: keyvault.outputs.keyvaultId
    storageAccountId: storage.outputs.storageId
  }
  dependsOn: [
    azResourceGroup
    keyvault
    containerRegistry
    applicationInsights
    storage
  ]
}

resource logAnalyticsResourceGroup 'Microsoft.Resources/resourceGroups@2021-04-01' = {
  dependsOn: []
  name: logAnalyticsResourceGroupName
  location: location
}

module logAnalyticsWorkspace './modules/logAnalytics.bicep' = {
  dependsOn: [
    logAnalyticsResourceGroup
  ]
  name: logAnalyticsWorkspaceName
  scope: resourceGroup(logAnalyticsResourceGroupName)
  params: {
    location: location
    prefix: 'la-${name}'
    tags: tags
  }
}
