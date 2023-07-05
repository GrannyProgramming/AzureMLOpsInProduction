// Creates an Azure Log Analytics workspace
@description('Azure region of the deployment')
param location string

@description('Tags to add to the resources')
param tags object

param prefix string
var uniqueSuffix = substring(uniqueString(resourceGroup().id), 0, 4)
var logAnalyticsWorkspaceName = '${prefix}-${uniqueSuffix}'

resource logAnalyticsWorkspace 'Microsoft.OperationalInsights/workspaces@2022-10-01' = {
  name: logAnalyticsWorkspaceName
  location: location
  tags: tags
  properties: {
    sku: {
      name: 'PerGB2018'
    }
  }
}

output logAnalyticsWorkspaceId string = logAnalyticsWorkspace.id
