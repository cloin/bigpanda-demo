DOCUMENTATION = r'''
module: bigpanda_incidents
short_description: Event-Driven Ansible source plugin to fetch active incidents from BigPanda
description:
    - Fetches active incidents from BigPanda API asynchronously
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
'''
import aiohttp
import asyncio
import os
from datetime import datetime, timedelta

async def fetch_bigpanda_incidents(session, api_url, api_token, environment_id):
    url = api_url.format(environment_id=environment_id)
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {api_token}"
    }
    params = {"sort_by": "last_change", "page": 1, "page_size": 99, "query": "status != \"ok\""}

    async with session.get(url, headers=headers, params=params) as response:
        if response.status != 200:
            print(f"HTTP Status Code: {response.status}")
            print("Response Text:", await response.text())
            return None
        return await response.json()

async def main(queue: asyncio.Queue, args: dict):
    interval = int(args.get("interval", 60))
    api_token = args.get("api_token")
    environment_id = args.get("environment_id")
    api_url = args.get("api_url", "https://api.bigpanda.io/resources/v2.0/environments/{environment_id}/incidents")

    incidents_record = {}  # dictionary to keep track of incidents

    async with aiohttp.ClientSession() as session:
        while True:
            response = await fetch_bigpanda_incidents(session, api_url, api_token, environment_id)
            if response and 'items' in response:
                for incident in response['items']:
                    incident_id = incident['id']
                    last_changed = max(incident.get('changed_at', 0), incident.get('updated_at', 0))

                    # check if the incident is new or has been updated since last checked
                    if incident_id not in incidents_record or incidents_record[incident_id] != last_changed:
                        await queue.put(incident)  # put the incident in the queue
                        incidents_record[incident_id] = last_changed  # update the record

            await asyncio.sleep(interval)

if __name__ == "__main__":
    args = {
        "api_token": os.getenv("BIGPANDA_API_TOKEN"),
        "environment_id": os.getenv("BIGPANDA_ENVIRONMENT_ID"),
        "api_url": os.getenv("BIGPANDA_API_URL", "https://api.bigpanda.io/resources/v2.0/environments/{environment_id}/incidents"),
        "interval": os.getenv("INTERVAL", "5"),
    }

    class MockQueue:
        async def put(self, incidents):
            print(incidents)

    asyncio.run(main(MockQueue(), args))
