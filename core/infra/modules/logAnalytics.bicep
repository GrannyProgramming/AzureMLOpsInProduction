param location string
param prefix string
var uniqueSuffix = substring(uniqueString(resourceGroup().id), 0, 4)
var logAnalyticsWorkspaceName = '${prefix}-${uniqueSuffix}'
@description('Tags to apply to the log analytics Instance')
param tags object = {}

resource logAnalyticsWorkspace 'Microsoft.OperationalInsights/workspaces@2020-08-01' = {
  name: logAnalyticsWorkspaceName
  location: location
  tags: tags
}

output logAnalyticsWorkspaceId string = logAnalyticsWorkspace.id
