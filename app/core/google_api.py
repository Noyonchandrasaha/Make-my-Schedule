from googleapiclient.discovery import build

def get_calendar_service(credentials):
    return build("calendar", "v3", credentials=credentials)
