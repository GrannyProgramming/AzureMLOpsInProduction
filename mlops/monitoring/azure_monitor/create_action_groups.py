import sys
import os
from azure.mgmt.monitor.models import (ActionGroupResource, EmailReceiver, SmsReceiver, WebhookReceiver, AzureAppPushReceiver,
                                       AutomationRunbookReceiver, VoiceReceiver, AzureFunctionReceiver, LogicAppReceiver,
                                       ArmRoleReceiver)
from workflow_utils.workflow_utils import setup_logger, log_event, load_config
from workflow_utils.pyclientauth import initialize_client

def create_action_group(monitor_client, resource_group, action_group, logger):
    receivers = {
        'email_receivers': [],
        'sms_receivers': [],
        'webhook_receivers': [],
        'azure_app_push_receivers': [],
        'automation_runbook_receivers': [],
        'voice_receivers': [],
        'logic_app_receivers': [],
        'azure_function_receivers': [],
        'arm_role_receivers': []
    }

    for receiver_type, receiver_values in action_group['receivers'].items():
        for value in receiver_values:
            if receiver_type == 'email':
                receivers['email_receivers'].append(EmailReceiver(name=value, email_address=value))
            elif receiver_type == 'sms':
                receivers['sms_receivers'].append(SmsReceiver(name=value['name'], country_code=value['country_code'], phone_number=value['phone_number']))
            elif receiver_type == 'webhook':
                receivers['webhook_receivers'].append(WebhookReceiver(name=value, service_uri=value))
            elif receiver_type == 'azure_app_push':
                receivers['azure_app_push_receivers'].append(AzureAppPushReceiver(name=value['name'], email_address=value['email_address']))
            elif receiver_type == 'voice':
                receivers['voice_receivers'].append(VoiceReceiver(name=value['name'], country_code=value['country_code'], phone_number=value['phone_number']))
            elif receiver_type == 'azure_function':
                receivers['azure_function_receivers'].append(AzureFunctionReceiver(**value))
            elif receiver_type == 'logic_app':
                receivers['logic_app_receivers'].append(LogicAppReceiver(**value))
            elif receiver_type == 'arm_role':
                receivers['arm_role_receivers'].append(ArmRoleReceiver(**value))
            elif receiver_type == 'automation_runbook':
                receivers['automation_runbook_receivers'].append(AutomationRunbookReceiver(**value))

    action_group_resource = ActionGroupResource(
        location=action_group['location'],
        group_short_name=action_group['action_group_name'],
        enabled=True,
        **receivers
    )
    
    try:
        monitor_client.action_groups.create_or_update(resource_group, action_group['action_group_name'], action_group_resource)
        log_event(logger, 'info', f"Successfully created/updated ActionGroup: {action_group['action_group_name']}")
    except Exception as err:
        if 'already exists' in str(err):
            log_event(logger, 'info', f"ActionGroup {action_group['action_group_name']} already exists.")
        else:
            log_event(logger, 'error', f"Error occurred while creating/updating ActionGroup: {action_group['action_group_name']}. Error: {err}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python script.py <filepath>")
        sys.exit(1)

    filepath = sys.argv[1]

    data = load_config(filepath)

    monitor_client = initialize_client("monitor")
    resource_group = os.getenv('LAW_RG')
    logger = setup_logger(__name__)
    for action_group in data['action_groups']:
        create_action_group(monitor_client, resource_group, action_group, logger)

if __name__ == '__main__':
    main()