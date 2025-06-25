import asyncio
from typing import Annotated, Optional
from langchain_core.tools import Tool, StructuredTool
from app.core.auth import get_token
from app.core.google_calendar_crud import (
    get_calendar_service,
    create_event,
    list_events,
    update_event,
    delete_event,
    find_event_by_title
)
from datetime import datetime

USER_ID = "user123"

# Ensure the date is in the future (for date-only input)
def ensure_future_datetime(date_str: str, time_str: str) -> str:
    try:
        now = datetime.now()
        dt = datetime.strptime(f"{date_str}T{time_str}", "%Y-%m-%dT%H:%M:%S")
        if dt < now:
            dt = dt.replace(year=now.year + 1)
        return dt.isoformat()
    except Exception:
        return None

# Async event listing tool
async def list_events_tool_func(max_results: int = 5):
    credentials = get_token(USER_ID)
    if not credentials:
        return "User not authenticated."

    service = get_calendar_service(credentials)
    now_iso = datetime.utcnow().isoformat() + "Z"
    events = list_events(service, max_results=max_results, time_min=now_iso)
    if isinstance(events, dict) and "error" in events:
        return f"Error: {events['error']}"

    if not events:
        return "No upcoming events found."

    formatted_events = []
    for event in events:
        start = event.get("start", {}).get("dateTime", event.get("start", {}).get("date", "No start time"))
        summary = event.get("summary", "No Title")
        formatted_events.append(f"- {summary} at {start}")

    return "\n".join(formatted_events)

# Async create event tool with timezone and datetime validation
async def create_event_tool_func(
    summary: Annotated[str, "Title of the event."],
    start_time: Annotated[str, "Start time in ISO format (e.g., 2025-06-28T15:00:00)"],
    end_time: Annotated[str, "End time in ISO format (e.g., 2025-06-28T16:00:00)"],
    time_zone: Annotated[str, "Time zone, e.g., 'Asia/Dhaka'"] = "Asia/Dhaka"
):
    credentials = get_token(USER_ID)
    if not credentials:
        return "User not authenticated."

    try:
        start_dt = datetime.fromisoformat(start_time)
        end_dt = datetime.fromisoformat(end_time)
        if start_dt < datetime.now():
            start_dt = start_dt.replace(year=start_dt.year + 1)
            end_dt = end_dt.replace(year=end_dt.year + 1)
            start_time = start_dt.isoformat()
            end_time = end_dt.isoformat()
    except ValueError:
        return "Invalid datetime format. Please use ISO format: YYYY-MM-DDTHH:MM:SS"

    service = get_calendar_service(credentials)

    event_body = {
        "summary": summary,
        "start": {
            "dateTime": start_time,
            "timeZone": time_zone
        },
        "end": {
            "dateTime": end_time,
            "timeZone": time_zone
        },
        "reminders": {
            "useDefault": True
        }
    }

    event = create_event(service, event_body)
    if isinstance(event, dict) and "error" in event:
        return f"Error: {event['error']}"

    return f"✅ Event '{summary}' created successfully from {start_time} to {end_time} ({time_zone})."

# Sync wrapper for list events
def list_events_tool_func_sync(max_results: int = 5):
    return asyncio.run(list_events_tool_func(max_results))

# Sync wrapper for create event tool
def create_event_tool_func_sync(
    summary: str,
    start_time: str,
    end_time: str,
    time_zone: str = "Asia/Dhaka"
):
    return asyncio.run(create_event_tool_func(summary, start_time, end_time, time_zone))

# Define the tools
ListEventsTool = Tool(
    name="list_events",
    func=list_events_tool_func_sync,
    description="List your next calendar events. Optionally takes the number of events to return."
)

CreateEventTool = StructuredTool.from_function(
    func=create_event_tool_func_sync,
    name="create_event",
    description="Create a calendar event by specifying title, start time, end time, and optionally time zone."
)

# --- New: Async update event by title ---
async def update_event_tool_func(
    title: str,
    new_summary: Optional[str] = None,
    new_start_time: Optional[str] = None,
    new_end_time: Optional[str] = None,
    time_zone: str = "Asia/Dhaka"
):
    credentials = get_token(USER_ID)
    if not credentials:
        return "User not authenticated."

    service = get_calendar_service(credentials)
    event = find_event_by_title(service, title)
    if not event:
        return f"No event found with title '{title}'."

    updated_event_body = event.copy()

    if new_summary:
        updated_event_body["summary"] = new_summary
    if new_start_time:
        updated_event_body["start"] = {"dateTime": new_start_time, "timeZone": time_zone}
    if new_end_time:
        updated_event_body["end"] = {"dateTime": new_end_time, "timeZone": time_zone}

    updated_event = update_event(service, event["id"], updated_event_body)
    if isinstance(updated_event, dict) and "error" in updated_event:
        return f"Error updating event: {updated_event['error']}"

    return f"✅ Event '{title}' updated successfully."

# --- New: Async delete event by title ---
async def delete_event_tool_func(title: str):
    credentials = get_token(USER_ID)
    if not credentials:
        return "User not authenticated."

    service = get_calendar_service(credentials)
    event = find_event_by_title(service, title)
    if not event:
        return f"No event found with title '{title}'."

    result = delete_event(service, event["id"])
    if isinstance(result, dict) and "error" in result:
        return f"Error deleting event: {result['error']}"

    return f"✅ Event '{title}' deleted successfully."

# --- Sync wrappers ---
def update_event_tool_func_sync(
    title: str,
    new_summary: Optional[str] = None,
    new_start_time: Optional[str] = None,
    new_end_time: Optional[str] = None,
    time_zone: str = "Asia/Dhaka"
):
    return asyncio.run(update_event_tool_func(title, new_summary, new_start_time, new_end_time, time_zone))

def delete_event_tool_func_sync(title: str):
    return asyncio.run(delete_event_tool_func(title))

# --- Define Tools ---
UpdateEventTool = StructuredTool.from_function(
    func=update_event_tool_func_sync,
    name="update_event",
    description="Update a calendar event by title. You can change summary, start time, and end time."
)

DeleteEventTool = StructuredTool.from_function(
    func=delete_event_tool_func_sync,
    name="delete_event",
    description="Delete a calendar event by title."
)
