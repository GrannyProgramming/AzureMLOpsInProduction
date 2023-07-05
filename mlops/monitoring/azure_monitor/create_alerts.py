import os
import sys
from datetime import timedelta
from azure.mgmt.monitor.v2022_08_01_preview.models  import Condition, ScheduledQueryRuleCriteria, ScheduledQueryRuleResource, Actions
from workflow_utils.workflow_utils import setup_logger, log_event, load_config
from workflow_utils.pyclientauth import initialize_client


def parse_time(time_str):
    """Parse time strings ending with 'h' or 'd' into value and unit."""
    unit = 'hours' if time_str[-1] == 'h' else 'days'
    value = int(time_str[:-1])
    return value, unit


def create_alert(monitor_client, resource_client, resource_group, subscription_id, workspace_name, alert_data):
    """Create alert."""
    # Define condition
    condition = Condition(
        time_aggregation=alert_data['condition']['time_aggregation'],
        operator=alert_data['condition']['operator'],
        threshold=alert_data['condition']['threshold'],
        query=alert_data['condition']['query'],
        metric_measure_column=alert_data['condition']['metric_measure_column']
    )

    # Define rule criteria
    rule_criteria = ScheduledQueryRuleCriteria(all_of=[condition])

    # Parse evaluation_frequency and window_size to handle 'h' and 'd'
    evaluation_frequency_value, evaluation_frequency_unit = parse_time(alert_data['evaluation_frequency'])
    window_size_value, window_size_unit = parse_time(alert_data['window_size'])

    # Get the location of the workspace
    workspace = resource_client.resources.get_by_id(
        f"/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.OperationalInsights/workspaces/{workspace_name}",
        '2022-10-01')
    workspace_location = workspace.location
    action_group_ids = [
    f"/subscriptions/{subscription_id}/resourcegroups/{resource_group}/providers/microsoft.insights/actiongroups/ag_log_app"
    ]


    actions = Actions(action_groups=action_group_ids, custom_properties={"key1:" "value1", "key2:" "value2"})

    # Define alert resource
    alert = ScheduledQueryRuleResource(
        location="eastus",
        description=alert_data['description'],
        display_name=alert_data['alert_name'],
        severity=alert_data['severity'],
        enabled=True,
        scopes=[
            f"/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.OperationalInsights/workspaces/{workspace_name}"],
        evaluation_frequency=timedelta(**{evaluation_frequency_unit: evaluation_frequency_value}),
        window_size=timedelta(**{window_size_unit: window_size_value}),
        actions=actions,
        criteria=rule_criteria
    )

    # Create or update the alert
    monitor_client.scheduled_query_rules.create_or_update(resource_group_name=resource_group,
        rule_name=alert_data['alert_name'],
        parameters=alert)


def main(file_path):
    """Main function."""
    # Create a monitor management client.
    resource_group = os.environ.get("LAW_RG")
    subscription_id = os.environ.get("SUBSCRIPTION_ID")
    workspace_name = os.environ.get("LAW_NAME")

    monitor_client = initialize_client("monitor")
    resource_client = initialize_client("resource")

    data = load_config(file_path)
    for alert in data['alerts']:
        create_alert(monitor_client, resource_client, resource_group, subscription_id, workspace_name, alert)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script_name.py <path_to_alerts_json>")
        sys.exit(1)

    json_file_path = sys.argv[1]
    main(json_file_path)
