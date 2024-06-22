from django.shortcuts import render
from django.http import HttpResponse
from rest_framework import generics
from api.models import Api_response
from api.serializer import ApiSerializer
from django.http import JsonResponse, HttpResponseBadRequest
import json
import google.generativeai as genai
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os
from dotenv import load_dotenv
from rest_framework.decorators import api_view

load_dotenv()  # Load environment variables from .env file

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar"]
APPLICATION_NAME = 'slack easy meet'

class BotSettings(generics.ListCreateAPIView):
    queryset = Api_response.objects.all()
    serializer_class = ApiSerializer


def create_calender_event(event_description, event_start, event_end):
    #    Shows basic usage of the Google Calendar API.

    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            flow.user_agent = APPLICATION_NAME
    creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("token.json", "w") as token:
        token.write(creds.to_json())

    try:
        service = build("calendar", "v3", credentials=creds)

        # Call the Calendar API
        event = {
            # 'summary': 'Google I/O 2015',
            # 'location': '800 Howard St., San Francisco, CA 94103',
            # 'description': 'A chance to hear more about Google\'s developer products.',
            'description': f'{event_description}',
            'start':
                f'{event_start}',
            'end':
                f'{event_end}',
            # 'attendees': [
            #     {'email': 'lpage@example.com'},
            #     {'email': 'sbrin@example.com'},
            # ],
            # 'reminders': {
            #     'useDefault': False,
            #     'overrides': [
            #         {'method': 'email', 'minutes': 24 * 60},
            #         {'method': 'popup', 'minutes': 10},
            #     ],
            # },
        }
        event = service.events().insert(calendarId='primary', body=event).execute()
        print(event.get('htmlLink'))

    except HttpError as error:
        print(f"An error occurred: {error}")

    


def format_slack_command(command_text):
    genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

    model = genai.GenerativeModel(
        'gemini-1.5-flash', generation_config={"response_mime_type": "application/json"})
    chat = model.start_chat(history=[])

    response = chat.send_message("""           Your job is to take a Slack command string as input and return a dictionary with three keys:
                    description: A string representing the description of the event extracted from the command.
                    start: A dictionary with two keys:
                    dateTime: A string representing the start date and time of the event in ISO 8601 format with timezone offset (e.g., '2024-06-07T16:09:00-04:00').
                    timeZone: A string representing the timezone of the event (e.g., 'America/Los_Angeles').
                    end: A dictionary with the same structure as start, representing the end date and time of the event (if provided in the command).
                    You should handle commands in natural language format, including:

                    Optional keywords like 'meeting', 'event', 'at', 'from', 'to'.
                    Time formats like '9:00 AM', '10:00', '17:30' (24-hour format).
                    Dates can be specified explicitly (e.g., "June 7th") or implicitly for today's date.
                    return only the dictionary as output, do not add anything else.
                        
                    Example:

                    Input Slack command: Team meeting today at 10 AM - 11 AM. Discuss new project ideas.

                    Output :
                    {
                    'description': 'Discuss new project ideas.',
                    
                    'start': {
                        'dateTime': '2024-06-07T10:00:00-04:00',
                        'timeZone': 'Africa/Lagos',

                    },
                    'end': {
                        'dateTime': '2024-06-07T11:00:00-04:00',
                        'timeZone': 'Africa/Lagos',

                    }
                    }
                                

                    Relpy using this JSON schema:
                                {
                    'description': 'Discuss new project ideas.',
                    
                    'start': {
                        'dateTime': '2024-06-07T10:00:00-04:00',
                        'timeZone': 'Africa/Lagos',

                    },
                    'end': {
                        'dateTime': '2024-06-07T11:00:00-04:00',
                        'timeZone': 'Africa/Lagos',

                    }
                    }
                    """)
    # print(response.text)

    response = chat.send_message(
        command_text)
    print(response.text)
    string_dict = response.text

    # using json.loads to convert string to dictionary
    try:
        dict_obj = json.loads(string_dict)
        print(dict_obj["description"])
        event_description = dict_obj["description"]
        event_start = dict_obj["start"]
        event_end = dict_obj["end"]

        create_calender_event(event_description, event_start, event_end)
    except (json.JSONDecodeError):
        print("invalid JSON format in the string")


@api_view(('POST',))
def handle_slack_event(request):
    """
    This view handles incoming Slack events and responds with a message.
    """
    if request.method != 'POST':
        return HttpResponseBadRequest(content="Invalid request method")

    try:
        # Parse request body
        # data = json.loads(request.body)
        data = request.POST
        # response_url = data.get('response_url')
        # user_id = data.get('user_id')
        # command_text = data.get('text')
        # print(f'command_text : {command_text}')
    except json.JSONDecodeError:
        return HttpResponseBadRequest(content="Invalid JSON data")
    command_text = "meeting with Samson on slack app development on 22nd August for an hour by 9pm"
    format_slack_command(command_text)

    # Build response payload

    # blocks = [
    #     {
    #         "type": "section",
    #         "text": {
    #             "type": "mrkdwn",
    #             "text": f"Hello, <@{user_id}>! Your reminder has been set!",
    #         },
    #     },
    # ]
    # payload = {
    #     "response_type": "ephemeral",  # sends response only to user that invoked command
    #     "blocks": blocks,
    #     "text": "Reminder successfully created",
    # }

    # # Send response to Slack
    # headers = {
    #     'Content-Type': 'application/json',
    # }
    # response = requests.post(response_url, headers=headers, json=payload)
    # response.raise_for_status()  # Raise exception for non-200 status codes

    return JsonResponse({}, status=200)
