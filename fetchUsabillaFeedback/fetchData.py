#!/usr/bin/python3

from __future__ import print_function
import pathlib
from googleapiclient.discovery import build
from google.oauth2 import service_account
import usabilla as ub
from datetime import datetime, timedelta, date
import json
import csv

NUM_DAYS = 30
OFFLINE = False

spreadsheetIds = {'Usabilla GS' : '17sPgywLbVhnXrQyTvU7dNP_-yY78ty9Cxy-dGwckn-Y'}
status_range = "'Script Results'"

platforms = {
    'ios': {'id': '5a6a634cb81f1c2e792c93c0', 'name': 'Beachbody On Demand - iOS - EN', 'range': "'Usabilla iOS BOD'", 'cache': '.cached_ios_feedbacks.json'},
    'android': {'id': '5c633e0b00caca56f3426cb7', 'name': 'Beachbody On Demand - Android - EN', 'range': "'Usabilla Android BOD'", 'cache': '.cached_android_feedbacks.json'},
    'web': {'id': '1e457a7fb8ed', 'name': 'BOD SPEECH BUBBLE FEEDBACK', 'range': "'Usabilla Raw Web'", 'cache': '.cached_web_feedbacks.json'}
}


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

def flatten_json(y): 
    out = {} 
  
    def flatten(x, name =''): 
        if type(x) is dict:   
            for a in x: 
                flatten(x[a], name + a + '_') 
        # If the Nested key-value 
        # pair is of list type 
        elif type(x) is list: 
              
            i = 0
              
            for a in x:                 
                flatten(a, name + str(i) + '_') 
                i += 1
        else: 
            out[name[:-1]] = x
    flatten(y) 
    return out 


def get_feedback(platform):
    first_form = platforms[platform]
    # Create an API client with access key and secret key
    api = ub.APIClient('5efa17767d11f58e', '5b9fd572688ceecf677f')

    print ('...Loading data', end='\r')

    # Set a limit for last X days
    epoch = datetime(1970, 1, 1)
    since = timedelta(days=NUM_DAYS)
    since_unix = (datetime.utcnow() - since - epoch).total_seconds() * 1000
    api.set_query_parameters({'since': int(since_unix)})

    print ('Loading feedbacks for ', first_form['name'], '...', end='\r')

    # Get the feedback of the first app form
    feedbacks_list = list()
    feedback = api.get_resource(
        api.SCOPE_LIVE,
        api.PRODUCT_WEBSITES if platform == 'web' else api.PRODUCT_APPS,
        api.RESOURCE_FEEDBACK,
        first_form['id'],
        iterate=True)
    feedbacks_list.append([item for item in feedback])
    with open(platforms[platform]['cache'], 'w') as f:
            json.dump(feedbacks_list[0], f)
            print ('cached', len(feedbacks_list[0]), 'feedbacks updated for', platform, ' ' * 20, end='\n')
    return feedbacks_list[0]

def export(platform):
    filename = platforms[platform]['cache'] 
    try:
        with open(filename, 'r') as f:
                feedbacks_list = json.load(f)
                print ('...reading from cache', end='\r')
    except:
        if platform in platforms:
            feedbacks_list = get_feedback(platform)
        else :
            print ('error, no imported data')
        print ('No cache, connecting to Usabilla...', end='\r')

    # format for GoogleSheets export
    print ('...preparing data for Google Sheets', end='\r')
    
    if platform == 'web':
        numbermap = {'date':1, 'custom_feedback_category':2, 'custom_issue_type':3, 'comment':4, 'email':5, 'browser_devicetype':6, 'browser_name':7, 'browser_os':8, 'browser_version':9, 'custom_Platform':10, 'publicUrl':11, 'id':12  }
    else:
         numbermap =  {'date':1, 'data_improvement_0':2, 'data_comment':3, 'appVersion':4, 'deviceName':5, 'osName':6, 'osVersion':7, 'language':8, 'screenshot':9, 'data_email':10,'id':11}
    final_dict = {}
    values = []
    for feedback_dict in feedbacks_list:
        flat_dict = flatten_json(feedback_dict)
        for item in flat_dict:
            if item == 'date':
                flat_dict[item]=flat_dict[item][:10]
            if item in numbermap:
                final_dict[item] = flat_dict[item]
            else:
                continue
            final_list = [final_dict[k] for k in sorted(final_dict, key = numbermap.__getitem__)]
            categories_list = sorted(final_dict, key = numbermap.__getitem__)
        if not values:
            values.append(categories_list)
        values.append(final_list)
    return values
def read_csv(filename):
    values = []
    with open(filename) as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        for row in readCSV:
            values.append(row)
    return values

title = """
  _   _ ___   _   ___ ___ _    _      _   
 | | | / __| /_\ | _ )_ _| |  | |    /_\  
 | |_| \__ \/ _ \| _ \| || |__| |__ / _ \ 
  \___/|___/_/ \_\___/___|____|____/_/ \_\ 
"""

if __name__ == '__main__':

    print(title)
    
    # Authorize with google sheets
    SERVICE_ACCOUNT_FILE = str(pathlib.Path(__file__).parent.resolve()) + '/keys.json'
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    SPREADSHEET_ID = '17sPgywLbVhnXrQyTvU7dNP_-yY78ty9Cxy-dGwckn-Y'
    service = build('sheets', 'v4', credentials=creds)

    # Update pre-execution status
    status = [[str(datetime.now())[0:-3], '', str(OFFLINE), 'ERROR']]
    status_request = service.spreadsheets().values().append(spreadsheetId=SPREADSHEET_ID, range=status_range, valueInputOption='RAW', body={ 'range' : status_range, 'majorDimension' : 'ROWS' , 'values': status })
    status_response = status_request.execute()
    status_range = status_response['updates']['updatedRange'].replace('A', 'B')

    for platform in platforms:
        if(not OFFLINE):
            get_feedback(platform)
        values = export(platform)
        sheets(service, values, spreadsheetIds['Usabilla GS'], platforms[platform]['range'], status_range)

    print("https://docs.google.com/spreadsheets/d/17sPgywLbVhnXrQyTvU7dNP_-yY78ty9Cxy-dGwckn-Y/edit#gid=1747113489") 

