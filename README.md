# BigPanda Incidents Ansible Plugin

This collection contains an event source plugin, rulebook(s) and plyabook(s) to demonstration Event-Driven Ansible and Bigpanda.

## Overview
This Ansible plugin is designed to fetch active incidents from BigPanda API asynchronously. It fetches activities for each incident and creates new events for new activities detected since the last polling. This plugin is part of an Event-Driven Ansible setup, allowing for real-time monitoring and response to BigPanda incident events.

## Requirements
- Python 3.7 or higher
- `aiohttp` library
- Access to BigPanda API (API token and Environment ID required)

## Configuration
The plugin can be configured through the Ansible rulebook. The following options are available:

- `api_token`: Your BigPanda API token (required).
- `environment_id`: Your BigPanda Environment ID (required).
- `api_url`: The URL for the BigPanda API. Defaults to `"https://api.bigpanda.io/resources/v2.0/environments/{environment_id}/incidents"`.
- `interval`: The interval, in seconds, at which the script polls the API. Defaults to `60`.
- `return_first_poll`: Whether to return all activities in the first poll. Defaults to `false`.

## Usage
To use this plugin, include it in your Ansible rulebook configuration. A sample configuration is provided below:

```yaml
- name: Monitor BigPanda incidents
  hosts: all
  sources:
    - cloin.bigpanda.bigpanda_incidents:
        api_token: <your_api_token>
        environment_id: <your_environment_id>
        api_url: https://api.bigpanda.io/resources/v2.0/environments/{environment_id}/incidents
        interval: 60
        return_first_poll: false
```

## Sample output

When combined with `ansible-rulebook`, the plugin provides detailed output for incident events. Below is a sample output:

```
[root@codespaces-cdacfb bigpanda-demo]# ansible-rulebook -i rulebooks/inventory.yml -r rulebooks/bigpanda_incidents.yml -S extensions/eda/plugins/event_source/

====================================================================================================================================================
kwargs:
{'hosts': ['all'],
 'inventory': 'rulebooks/inventory.yml',
 'project_data_file': None,
 'rule': 'R1 - Debug all',
 'rule_run_at': '2023-11-16T16:29:15.960959Z',
 'rule_set': 'Bigpanda incident events',
 'rule_set_uuid': 'e8af3a51-31ea-40c7-b9e1-35456916624c',
 'rule_uuid': '1c5e69be-440c-4785-82b6-797c91dec557',
 'variables': {'event': {'activity': {'created_by': '6553d04d2463e49f8eb3c771',
                                      'id': '83811b32d1292efa7b4da1e84898151b',
                                      'params': {'comment': 'Brand new comment '
                                                            'on this incident! '
                                                            '<3 Event-Driven '
                                                            'Ansible'},
                                      'timestamp': 1700152154,
                                      'type': 'incident_commented'},
                         'incident': {'active': True,
                                      'alerts': [{'alert_id': '65397b2eede0a80012631b0c'}],
                                      'assignee': {'email': 'colin@redhat.com',
                                                   'name': 'Colllin',
                                                   'user_id': '6553d04d2463e49f8eb3c771'},
                                      'assigner': {'email': 'colin@redhat.com',
                                                   'name': 'Colllin',
                                                   'user_id': '6553d04d2463e49f8eb3c771'},
                                      'changed_at': 1698265901,
                                      'correlation_matchers_log': [[]],
                                      'end': None,
                                      'environments': ['124312341234',
                                                       '567856785678'],
                                      'flapping': False,
                                      'folders': ['active',
                                                  'shared',
                                                  'assigned'],
                                      'id': '653989e52d00001901351684',
                                      'incident_tags': [],
                                      'maintenance': None,
                                      'severity': 'Critical',
                                      'shared': True,
                                      'snooze': {'snoozed': False},
                                      'start': 1698265901,
                                      'status': 'Critical',
                                      'updated_at': 1700061365},
                         'meta': {'received_at': '2023-11-16T16:29:15.918854Z',
                                  'source': {'name': 'bigpanda_incidents',
                                             'type': 'bigpanda_incidents'},
                                  'uuid
```