param location string

@description('Tags to add to the resources')
param tags object = {}
param prefix string
var uniqueSuffix = substring(uniqueString(resourceGroup().id), 0, 4)
var applicationInsightsName = '${prefix}-${uniqueSuffix}'


resource applicationInsights 'Microsoft.Insights/components@2020-02-02-preview' = {
  name: applicationInsightsName
  location: location
  tags: tags
  kind: 'web'
  properties: {
    Application_Type: 'web'
    DisableIpMasking: false
    DisableLocalAuth: false
    Flow_Type: 'Bluefield'
    ForceCustomerStorageForProfiler: false
    ImmediatePurgeDataOn30Days: true
    IngestionMode: 'ApplicationInsights'
    publicNetworkAccessForIngestion: 'Enabled'
    publicNetworkAccessForQuery: 'Disabled'
    Request_Source: 'rest'
  }
}

output applicationInsightsId string = applicationInsights.id
