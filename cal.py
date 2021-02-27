from __future__ import print_function
from notion.block import PageBlock
from notion.block import TodoBlock
from notion.client import NotionClient
from discord_webhook import DiscordWebhook
import dateutil.parser
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import logging
from dotenv import load_dotenv


def init():
    # Logger starting
    loggingFormat = "%(levelname)s: [%(asctime)s] %(message)s %(filename)s#%(lineno)s "
    logging.basicConfig(filename=".logging", level=logging.DEBUG, format=loggingFormat)
    logger = logging.getLogger()
    logging.info("Logger started")


def getVariable(key):
    load_dotenv()
    return os.getenv(key)


# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']


def _getGoodCreds():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return creds


def getEvents(limit=1000):

    creds = _getGoodCreds()
    service = build('calendar', 'v3', credentials=creds)

    # Call the Calendar API
    now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
    events_result = service.events().list(maxResults=limit, calendarId='54g7n4diedrddf8cdm11sl50mk5fj3r3@import.calendar.google.com', timeMin=now, singleEvents=True, orderBy='startTime').execute()
    events = events_result.get('items', [])

    return events


def sendToDiscord(text):
    _url = getVariable("DISORD_WEBHOOK")

    webhook = DiscordWebhook(url=_url, content=text)
    response = webhook.execute()


def callNotionAPI():
    token = getVariable(NOTION_TOKEN)
    db_url = "https://www.notion.so/shirobachi/020cfa41c8254c9196deb6e93d6f5ce0?v=5b4c4ff4e74e4614b1ea9d334204930a"
    pg_url = "https://www.notion.so/shirobachi/test-96d3090d48f746b98b36f6c2b0286d40"

    client = NotionClient(token_v2=token)
    db = client.get_collection_view(db_url)

    # row = db.collection.add_row()

    # events = getEvents(1)
    # time = events[0]['start'].get('dateTime')
    # dt = dateutil.parser.parse(time)
    # tmp = dt.strftime('%b %e, %Y')
    # row.Date = tmp
    # print(tmp)

    rows = db.collection.get_rows()
    for row in rows:
        print("created" + str(row.created))
        print("Date" + str(row.Date))
        print("date" + str(row.date))
        print("a" + str(row.a))


print(getVariable("DISORD_WEBHOOK"))

events = getEvents(12)

text = ""

for event in events:
    text += "- " + str(event['summary']) + "\n"

text = "Lista zajęć:\n"+text
print(text)
sendToDiscord(text)


# callNotionAPI()

# events = getEvents(1)
# messageSufix = events[0]['summary']

# sendToDiscord("Next class is " + messageSufix)


# if not events:
#     print('No upcoming events found.')
# for event in events:
#     start = event['start'].get('dateTime', event['start'].get('date'))

#     dt = dateutil.parser.parse(event['start'].get('dateTime'))
#     tmp = dt.strftime('%H:%M')
#     print(tmp, end="")
#     print(event['summary'])
