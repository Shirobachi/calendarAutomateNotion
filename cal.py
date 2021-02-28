from __future__ import print_function
from http.client import parse_headers
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
from notion.collection import NotionDate


def init():
    # Logger starting
    loggingFormat = "%(levelname)s: [%(asctime)s] %(message)s %(filename)s#%(lineno)s "
    logging.basicConfig(filename=".logging", level=logging.DEBUG, format=loggingFormat)
    logger = logging.getLogger()
    logging.info("Logger started")


def getVariable(key):
    load_dotenv()
    return os.getenv(key)
    logging.info("Loaded local varirabled")


def _getGoodCreds():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """

    # If modifying these scopes, delete the file token.pickle.
    SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

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
    logging.info("Creds succefully get")
    return creds


def getEvents(limit=1000):

    creds = _getGoodCreds()
    service = build('calendar', 'v3', credentials=creds)

    # Call the Calendar API
    now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
    # events_result = service.events().list(maxResults=limit, calendarId='54g7n4diedrddf8cdm11sl50mk5fj3r3@import.calendar.google.com', timeMin=now, singleEvents=True, orderBy='startTime').execute()
    events_result = service.events().list(maxResults=limit, calendarId='primary', timeMin=now, singleEvents=True, orderBy='startTime').execute()
    events = events_result.get('items', [])
    logging.info("Get events from google API")

    return events


def sendToDiscord(text):
    _url = getVariable("DISORD_WEBHOOK")

    webhook = DiscordWebhook(url=_url, content=text)
    response = webhook.execute()
    logging.info("Sent message by discord webhook")


def _stringToDate(data):

    dt = dateutil.parser.parse(data)
    str = dt.strftime("%Y-%m-%d %H:%M")
    result = datetime.datetime.strptime(str, "%Y-%m-%d %H:%M")

    return result


def callNotionAPI():
    token = getVariable("NOTION_TOKEN")

    return NotionClient(token_v2=token)


def parseName(input):
    output = "["
    temp = input.split(" - ")
    output += temp[0]
    output += "] "

    temp2 = temp[1].split(" ")
    for word in temp2:
        if len(word) > 1:
            output += word[0].upper()
        else:
            output += word
    logging.info("Parsed name")
    return output


init()
client = callNotionAPI()

db_url = "https://www.notion.so/shirobachi/0c79483ecf20424aa5a97781741ec185?v=ffa16d64036846c8b39eb9ac5300381c"
db = client.get_collection_view(db_url)

events = getEvents()

today = datetime.datetime.now().strftime("%d%m%Y")
today = datetime.datetime.strptime(today, "%d%m%Y")
today += datetime.timedelta(days=1)
today = today.strftime("%d%m%Y")

message = "Jutrzejsze zajęcia:\n"

for event in events:
    dt = dateutil.parser.parse(event['start']['dateTime'])
    eventStamp = dt.strftime("%d%m%Y")

    if today == eventStamp:

        start = _stringToDate(event['start']['dateTime'])
        end = _stringToDate(event['end']['dateTime'])
        startHour = dt.strftime("%H:%M")

        row = db.collection.add_row()
        row.title = today
        row.title = parseName(event['summary'])
        row.date = NotionDate(start, end=end)
        row.tags = "College"
        message += "- " + startHour + ": " + event['summary']
        if parseName(event['summary']) == "[WKLD] GK":
            message += " [ https://join.skype.com/aUFNC3LWFlpo ]"
        message += "\n"
    else:
        break

sendToDiscord(message)
