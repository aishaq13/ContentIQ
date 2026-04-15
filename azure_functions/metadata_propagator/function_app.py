"""Azure Functions-style event propagator.

This file illustrates how metadata events can be consumed by serverless workers
for low-latency propagation to edge caches or downstream systems.
"""

import json
import logging

import azure.functions as func

app = func.FunctionApp()


@app.event_hub_message_trigger(arg_name="event", event_hub_name="metadata-events", connection="EVENT_HUB_CONNECTION")
def propagate_metadata(event: func.EventHubEvent) -> None:
    payload = json.loads(event.get_body().decode("utf-8"))
    logging.info("Propagating metadata event key=%s version=%s", payload["record"]["key"], payload["record"]["version"])
