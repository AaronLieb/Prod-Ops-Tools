#!/usr/bin/python3

import pathlib
from googleapiclient.discovery import build
from google.oauth2 import service_account
from datetime import datetime, timedelta, date
import requests
import json
import csv

NUM_DAYS = 30
OFFLINE = False

spreadsheetIds = {'Usabilla GS' : '17sPgywLbVhnXrQyTvU7dNP_-yY78ty9Cxy-dGwckn-Y'}
ratings_range = 'Ratings Raw'
status_range = "'Ratings Script Results'"

def sheets(service, values, SPREADSHEET_ID, rangeName, status_range):
    
        id_column_index = values[0].index('id')

        column = chr(65 + id_column_index)

        # get the rows currently on the sheet
        get_request = service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID, range=rangeName + '!' + column + '2:' + column)
        get_response = get_request.execute()
        # get the ids from the sheet
        get_ids = []
        if ('values' in get_response):
            get_ids = sum(get_response['values'], [])
        # find the column that contains the ids
        id_column_index = values[0].index('id')
        # get the ids from the data we are trying to add to the sheet
        post_ids = [row[id_column_index] for row in values][1:]
        # subtract the data that is on both id lists, and add the remaining rows to a final list
        final_post = []
        for post_id in post_ids:
            if post_id not in get_ids:
                for row in values:
                    if row[id_column_index] == post_id:
                        final_post.append(row)

        # append the new rows to the spreadsheet
        post_request = service.spreadsheets().values().append(spreadsheetId=SPREADSHEET_ID, range=rangeName, valueInputOption='RAW', body={ 'range' : rangeName , 'majorDimension' : 'ROWS' , 'values': final_post })
        post_response = post_request.execute()

        # update post-execution status
        status = [[str(datetime.now())[0:-3], str(OFFLINE), 'COMPLETE']]
        status_request = service.spreadsheets().values().update(spreadsheetId=SPREADSHEET_ID, range=status_range, valueInputOption='RAW', body={ 'range' : status_range, 'majorDimension' : 'ROWS' , 'values': status })
        status_response = status_request.execute()
 
        print(rangeName, 'export completed.\n', len(final_post), "new rows were created\n")


def authorize(email, password):
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    params = {
            'url': 'https://beachbody.us.janraincapture.com/oauth/auth_native_traditional',
            'client_id': 'yj6pt5bdcg8rjkd2pkxuvdync84b8cmv',
            'locale': 'en-US',
            'redirect_uri': 'https://localhost',
            'response_type': 'code',
            'form': 'signInForm',
            'signInEmailAddress': email,
            'currentPassword': password, 
            }
    response = requests.post('https://beachbody.us.janraincapture.com/oauth/auth_native_traditional', params=params, headers=headers)
    print(response.json())
    



def get_ratings(auth_code):
    headers = {
            'x-api-key': 'CCOGMiX1XH2iaERs5LavL6UMo47OaYUu3f8n4o9P', 
            'Authorization': 'Bearer '}


    ratings = {}
    return ratings

if __name__ == '__main__':
    
    # Authorize with google sheets
    SERVICE_ACCOUNT_FILE = str(pathlib.Path(__file__).parent.resolve()) + '/keys.json'
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    SPREADSHEET_ID = '17sPgywLbVhnXrQyTvU7dNP_-yY78ty9Cxy-dGwckn-Y'
    service = build('sheets', 'v4', credentials=creds)

    # Update pre-execution status
    status = [[str(datetime.now())[0:-3], '', str(OFFLINE), 'ERROR']]
    status_request = service.spreadsheets().values().append(spreadsheetId=SPREADSHEET_ID, range=status_range, valueInputOption='RAW', body={ 'range' : status_range , 'majorDimension' : 'ROWS' , 'values': status })
    status_response = status_request.execute()
    new_status_range = status_response['updates']['updatedRange'].replace('A', 'B')
    
    auth_code = authorize('Tester_QA6_Free_Us@yopmail.com', 'Beach1234*')
    values = get_ratings(auth_code)
    sheets(service, values, spreadsheetIds['Usabilla GS'], ratings_range, new_status_range)

    print("https://docs.google.com/spreadsheets/d/17sPgywLbVhnXrQyTvU7dNP_-yY78ty9Cxy-dGwckn-Y/edit#gid=1747113489") 

