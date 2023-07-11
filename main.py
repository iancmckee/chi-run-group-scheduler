from __future__ import print_function

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# The ID and range of a sample spreadsheet.
# SAMPLE_SPREADSHEET_ID = '1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms'
SPREDSHEET_ID= '1qhBbsoIqtk4XoR2eNO4zQJU7RAtP-m_xcX4_hkO_nu0'
SAMPLE_RANGE_NAME = 'Responses!B2:C'
AVAILABILITIES ='Running_Day_options!A:A'


def pull_sheet_info():
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secret_425157155929-84flhqeljut0vo7riqpm7o0gpjtjj5hk.apps.googleusercontent.com.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('sheets', 'v4', credentials=creds)

        # Call the Sheets API
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=SPREDSHEET_ID,
                                    range=SAMPLE_RANGE_NAME).execute()
        available_days = sheet.values().get(spreadsheetId=SPREDSHEET_ID,
                                            range=AVAILABILITIES).execute()
        day_options = available_days.get('values',[])
        name_availability = result.get('values', [])

        days_names_map = {}
        # slow but works
        for day in day_options:
            days_names_map.update({day[0]:[]})
            # Cycle through each name in the list of availability and if it has this day, add it to the hashmap
            for name,avail_days in name_availability:
                if day[0] in avail_days:
                    days_names_map[day[0]].append(name)
        return days_names_map
    except HttpError as err:
        print(err)

# It doesn't have to be fast it just has to work
if __name__ == '__main__':
    avail_by_day = pull_sheet_info()
    days = list(avail_by_day.keys())
    best_days = {}
    max_attendees = 0
    #Two Pointer problem, make two sets, compare how many are in each set
    for idx, (day, attendees) in enumerate(avail_by_day.items()):
        day_set = set(attendees)
        pointer2 = idx+1
        while pointer2 <= len(days)-1:
            comp_day_set = set(avail_by_day.get(days[pointer2]))
            if len(day_set | comp_day_set) > max_attendees:
                max_attendees = len(day_set | comp_day_set)
                best_days = [{day:attendees}, {days[pointer2]:avail_by_day.get(days[pointer2])}]
            pointer2 += 1

    print(best_days)