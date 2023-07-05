// Creates an Azure Container Registry with Azure Private Link endpoint
@description('Azure region of the deployment')
param location string

@description('Tags to add to the resources')
param tags object

param prefix string 
var uniqueSuffix = substring(uniqueString(resourceGroup().id), 0, 4)
var containerRegistryName = '${prefix}-${uniqueSuffix}'
var containerRegistryNameCleaned = replace(containerRegistryName, '-', '')

resource containerRegistry 'Microsoft.ContainerRegistry/registries@2021-09-01' = {
  name: containerRegistryNameCleaned
  location: location
  tags: tags
  sku: {
    name: 'Standard'
  }
  properties: {
    adminUserEnabled: true
  }
}

output containerRegistryId string = containerRegistry.id
