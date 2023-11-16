DOCUMENTATION = r'''
module: bigpanda_incidents
short_description: Event-Driven Ansible source plugin to fetch active incidents from BigPanda
description:
    - Fetches active incidents from BigPanda API asynchronously
    - Fetches activities for each incident and creates new events for new activities
    - Parameters are passed from Ansible rulebook
author: "Colin McNaughton (@cloin)"
options:
    api_token:
        description:
            - Your BigPanda API token
        required: true
    environment_id:
        description:
            - Your BigPanda Environment ID
        required: true
    api_url:
        description:
            - The URL for the BigPanda API
        required: false
        default: "https://api.bigpanda.io/resources/v2.0/environments/{environment_id}/incidents"
    interval:
        description:
            - The interval, in seconds, at which the script polls the API
        required: false
        default: 60
    return_first_poll:
        description:
            - Whether to return all activities in the first poll
        required: false
        default: false
'''

EXAMPLES = r'''
- name: Monitor BigPanda incidents
  hosts: all
  sources:
    - cloin.bigpanda.bigpanda_incidents:
        api_token: your_api_token
        environment_id: your_environment_id
        api_url: https://api.bigpanda.io/resources/v2.0/environments/{environment_id}/incidents
        interval: 60
        return_first_poll: false
'''
import aiohttp
import asyncio
import os

async def fetch_activities(session, api_token, incident_id):
    """Fetch activities for a specific incident."""
    activities_url = f"https://api.bigpanda.io/resources/v2.0/incidents/{incident_id}/activities?page=1&per_page=99"
    headers = {"accept": "application/json", "Authorization": f"Bearer {api_token}"}

    async with session.get(activities_url, headers=headers) as response:
        if response.status != 200:
            print(f"Error fetching activities: HTTP Status Code: {response.status}")
            return []
        return await response.json()

async def fetch_bigpanda_incidents(session, api_url, api_token, environment_id):
    """Fetch incidents from BigPanda."""
    url = api_url.format(environment_id=environment_id)
    headers = {"accept": "application/json", "Authorization": f"Bearer {api_token}"}
    params = {"sort_by": "last_change", "page": 1, "page_size": 99, "query": "status != \"ok\""}

    async with session.get(url, headers=headers, params=params) as response:
        if response.status != 200:
            print(f"HTTP Status Code: {response.status}")
            print("Response Text:", await response.text())
            return None
        return await response.json()

async def main(queue: asyncio.Queue, args: dict):
    """Main function to poll incidents and activities."""
    interval = int(args.get("interval", 60))
    api_token = args.get("api_token")
    environment_id = args.get("environment_id")
    api_url = args.get("api_url", "https://api.bigpanda.io/resources/v2.0/environments/{environment_id}/incidents")
    return_first_poll = args.get("return_first_poll", False)

    activities_record = {}
    first_poll = True

    async with aiohttp.ClientSession() as session:
        while True:
            response = await fetch_bigpanda_incidents(session, api_url, api_token, environment_id)
            if response and 'items' in response:
                for incident in response['items']:
                    incident_id = incident['id']
                    activities = await fetch_activities(session, api_token, incident_id)
                    activities_list = activities.get('items', [])
                    
                    for activity in activities_list:
                        activity_id = activity['id']
                        if first_poll and not return_first_poll:
                            activities_record.setdefault(incident_id, set()).add(activity_id)
                        elif activity_id not in activities_record.get(incident_id, set()):
                            event = {'incident': incident, 'activity': activity}
                            await queue.put(event)
                            activities_record.setdefault(incident_id, set()).add(activity_id)

            first_poll = False
            await asyncio.sleep(interval)

if __name__ == "__main__":
    args = {
        "api_token": os.getenv("BIGPANDA_API_TOKEN"),
        "environment_id": os.getenv("BIGPANDA_ENVIRONMENT_ID"),
        "api_url": os.getenv("BIGPANDA_API_URL", "https://api.bigpanda.io/resources/v2.0/environments/{environment_id}/incidents"),
        "interval": os.getenv("INTERVAL", "60"),
        "return_first_poll": os.getenv("RETURN_FIRST_POLL", "false").lower() == "true"
    }

    class MockQueue:
        async def put(self, event):
            print(event)

    asyncio.run(main(MockQueue(), args))
