from datetime import datetime
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

def get_calendar_service(credentials):
    return build("calendar", "v3", credentials=credentials)

def create_event(service, event_body):
    try:
        event = service.events().insert(calendarId='primary', body=event_body).execute()
        return event
    except HttpError as error:
        return {"error": str(error)}

def list_events(service, max_results=10, time_min=None):
    try:
        params = {
            'calendarId': 'primary',
            'maxResults': max_results,
            'singleEvents': True,
            'orderBy': 'startTime'
        }
        if time_min:
            params['timeMin'] = time_min
        events_result = service.events().list(**params).execute()
        return events_result.get('items', [])
    except HttpError as error:
        return {"error": str(error)}

def update_event(service, event_id, updated_event_body):
    try:
        event = service.events().update(
            calendarId='primary', eventId=event_id, body=updated_event_body).execute()
        return event
    except HttpError as error:
        return {"error": str(error)}

def delete_event(service, event_id):
    try:
        service.events().delete(calendarId='primary', eventId=event_id).execute()
        return {"status": "deleted"}
    except HttpError as error:
        return {"error": str(error)}

def find_event_by_title(service, title: str, max_results=10):
    """
    Search for an upcoming event with exact title match (case insensitive).
    """
    now = datetime.utcnow().isoformat() + "Z"
    events = list_events(service, max_results=max_results, time_min=now)
    if isinstance(events, dict) and "error" in events:
        return None
    for event in events:
        summary = event.get("summary", "")
        if summary.strip().lower() == title.strip().lower():
            return event
    return None
