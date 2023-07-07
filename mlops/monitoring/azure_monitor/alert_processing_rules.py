import sys
import os
from workflow_utils.workflow_utils import load_config
from workflow_utils.pyclientauth import initialize_client

def create_action_rules(alert_groups, client, subscription_id, resource_group):
    for group in alert_groups:
        action_rule_name = group['action_group_name']
        resource_id = f"/subscriptions/{subscription_id}/resourcegroups/{resource_group}/providers/microsoft.insights/actiongroups/{action_rule_name}"
        action_rule = {
            "location": group['location'],
            "tags": {},
            "properties": {
                "type": "ActionGroup",
                "scope": {
                    "scopeType": "ResourceGroup",
                    "values": [f"/subscriptions/{subscription_id}/resourceGroups/{resource_group}"]
                },
                "conditions": {
                    "severityCondition": {
                        "operator": "Equals",
                        "values": group['severity']
                    }
                },
                "description": f"Add {action_rule_name} to all alerts with severity in {group['severity']}",
                "status": "Enabled",
                "action_group_id": resource_id,
            }
        }
        
        try:
            # Check if the action rule already exists
            existing_action_rule = client.action_rules.get(
                resource_group_name=os.environ["LAW_RG"],
                action_rule_name=action_rule_name,
            )
            print(f"Action rule {action_rule_name} already exists. Skipping creation.")
        except Exception:
            # If the action rule does not exist, create a new one
            client.action_rules.create_update(
                resource_group_name=os.environ["LAW_RG"],
                action_rule_name=action_rule_name,
                action_rule=action_rule
            )

def main(file_path):
    data = load_config(file_path)
    client = initialize_client("alerts")
    subscription_id = os.environ.get("SUBSCRIPTION_ID")
    resource_group = os.environ.get("LAW_RG")
    create_action_rules(data['action_groups'], client, subscription_id, resource_group)

if __name__ == "__main__":
    file_path = sys.argv[1]
    main(file_path)
