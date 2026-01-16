import os
import pickle
from datetime import datetime
from zoneinfo import ZoneInfo

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

SCOPES = ["https://www.googleapis.com/auth/calendar"]
TIMEZONE = ZoneInfo("Asia/Kolkata")


# ================= AUTH =================

def get_calendar_service():
    creds = None

    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )

            auth_url, _ = flow.authorization_url(prompt="consent")

            print("\nAUTHORIZE THIS APP")
            print(auth_url)
            print("\nPaste the authorization code here:")

            code = input("> ").strip()
            flow.fetch_token(code=code)
            creds = flow.credentials

        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)

    return build("calendar", "v3", credentials=creds)



# ================= MCP TOOLS =================

def list_events(start_date: str, end_date: str):
    service = get_calendar_service()

    start = datetime.fromisoformat(start_date).replace(
        tzinfo=TIMEZONE
    ).isoformat()

    end = datetime.fromisoformat(end_date).replace(
        tzinfo=TIMEZONE
    ).isoformat()

    events = service.events().list(
        calendarId="primary",
        timeMin=start,
        timeMax=end,
        singleEvents=True,
        orderBy="startTime",
        timeZone="Asia/Kolkata"
    ).execute()

    return events.get("items", [])


def search_events(keyword: str):
    service = get_calendar_service()
    events = service.events().list(
        calendarId="primary",
        q=keyword,
        singleEvents=True
    ).execute()

    return events.get("items", [])


def create_event(title, date, start_time, end_time, description="", location=""):
    service = get_calendar_service()

    start_dt = datetime.fromisoformat(
        f"{date}T{start_time}"
    ).replace(tzinfo=TIMEZONE)

    end_dt = datetime.fromisoformat(
        f"{date}T{end_time}"
    ).replace(tzinfo=TIMEZONE)

    event = {
        "summary": title,
        "description": description,
        "location": location,
        "start": {
            "dateTime": start_dt.isoformat(),
            "timeZone": "Asia/Kolkata"
        },
        "end": {
            "dateTime": end_dt.isoformat(),
            "timeZone": "Asia/Kolkata"
        }
    }

    created = service.events().insert(
        calendarId="primary",
        body=event
    ).execute()

    return {
        "status": "created",
        "event_id": created.get("id"),
        "summary": created.get("summary")
    }

