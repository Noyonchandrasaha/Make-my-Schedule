from typing import Optional, List
from pydantic import BaseModel
from app.core.auth import get_token
from app.core.google_calendar_crud import get_calendar_service, create_event, list_events
from datetime import datetime, timedelta
import asyncio
from app.langgraph.utils import parse_natural_datetime, ensure_future_datetime, format_event_datetime, default_event_color, default_event_status
from langchain_core.tools import StructuredTool

USER_ID = "user123"  # ideally dynamic per session

class Reminder(BaseModel):
    method: str
    minutes: int

class CreateEventInput(BaseModel):
    summary: str
    start_time: str
    end_time: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None
    color_id: Optional[str] = None
    status: Optional[str] = None
    reminders: Optional[List[Reminder]] = None

async def create_event_tool_func(
    summary: str,
    start_time: str,
    end_time: Optional[str] = None,
    location: Optional[str] = None,
    description: Optional[str] = None,
    color_id: Optional[str] = None,
    status: Optional[str] = None,
    reminders: Optional[List[dict]] = None,
):
    credentials = get_token(USER_ID)
    if not credentials:
        return "User not authenticated."

    service = get_calendar_service(credentials)

    # Parse and normalize start_time
    try:
        start_dt = parse_natural_datetime(start_time)
        start_dt = ensure_future_datetime(start_dt)
    except Exception as e:
        return f"Invalid start_time: {str(e)}"

    # Parse and normalize end_time or default to 30 min after start_time
    if end_time:
        try:
            end_dt = parse_natural_datetime(end_time)
            end_dt = ensure_future_datetime(end_dt)
        except Exception as e:
            return f"Invalid end_time: {str(e)}"
    else:
        end_dt = start_dt + timedelta(minutes=30)

    # Prevent creating events in the past
    now = datetime.now(tz=start_dt.tzinfo)
    if start_dt < now:
        return "Cannot create events in the past."

    # Conflict check - list events starting after start_time
    events = list_events(service, max_results=20, time_min=start_dt.isoformat() + "Z")
    if isinstance(events, dict) and "error" in events:
        return f"Error fetching existing events: {events['error']}"

    # Check overlap
    for event in events:
        ev_start_str = event.get("start", {}).get("dateTime") or event.get("start", {}).get("date")
        ev_end_str = event.get("end", {}).get("dateTime") or event.get("end", {}).get("date")
        if not ev_start_str or not ev_end_str:
            continue
        ev_start = datetime.fromisoformat(ev_start_str.replace("Z", "+00:00"))
        ev_end = datetime.fromisoformat(ev_end_str.replace("Z", "+00:00"))
        if (start_dt < ev_end) and (end_dt > ev_start):
            conflict_summary = event.get("summary", "Untitled event")
            conflict_start = ev_start.isoformat()
            conflict_end = ev_end.isoformat()
            return (
                f"⚠️ Conflict with existing event '{conflict_summary}' "
                f"from {conflict_start} to {conflict_end}. Please choose another time."
            )

    # Build event body
    event_body = {
        "summary": summary,
        "start": {
            "dateTime": format_event_datetime(start_dt),
            "timeZone": "Asia/Dhaka",
        },
        "end": {
            "dateTime": format_event_datetime(end_dt),
            "timeZone": "Asia/Dhaka",
        },
        "status": status or default_event_status(),
        "colorId": color_id or default_event_color("normal"),
    }

    if location:
        event_body["location"] = location
    if description:
        event_body["description"] = description
    if reminders:
        event_body["reminders"] = {
            "useDefault": False,
            "overrides": [{"method": r["method"], "minutes": r["minutes"]} for r in reminders],
        }
    else:
        event_body["reminders"] = {"useDefault": True}

    loop = asyncio.get_event_loop()
    try:
        event = await loop.run_in_executor(None, lambda: create_event(service, event_body))
    except Exception as e:
        return f"Error creating event: {str(e)}"

    if isinstance(event, dict) and "error" in event:
        return f"Error from Google API: {event['error']}"

    return f"✅ Event '{summary}' created successfully from {start_dt.isoformat()} to {end_dt.isoformat()}."

def create_event_tool_func_sync(**kwargs):
    import asyncio
    return asyncio.run(create_event_tool_func(**kwargs))

CreateEventTool = StructuredTool.from_function(
    func=create_event_tool_func_sync,
    name="create_event",
    description="Create a Google Calendar event with title, time, location, and more. Checks for conflicts and avoids past events."
)