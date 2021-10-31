import pandas as pd
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow,Flow
from google.auth.transport.requests import Request
import os
import pickle

# from https://medium.com/analytics-vidhya/how-to-read-and-write-data-to-google-spreadsheet-using-python-ebf54d51a72c

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# here enter the id of your google sheet
from dotenv import load_dotenv

load_dotenv()  
gsheetid = os.environ.get("GSHEET_ID")

SAMPLE_SPREADSHEET_ID_input = gsheetid
SAMPLE_RANGE_NAME = 'A1:K30'

def main():
    global values_input, service
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'my_json_file.json', SCOPES) # here enter the name of your downloaded JSON file
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    result_input = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID_input,
                                range=SAMPLE_RANGE_NAME).execute()
    values_input = result_input.get('values', [])

    if not values_input and not values_expansion:
        print('No data found.')

main()

df=pd.DataFrame(values_input[1:], columns=values_input[0])

print(df)

print("READING DONE")




df_gold=df[(df['level']=='60')] # & (df['Sport']=='Gymnastics')]

from dotenv import load_dotenv

load_dotenv()  
gsheetid = os.environ.get("GSHEET_ID")

SAMPLE_SPREADSHEET_ID_input = gsheetid


#change the range if needed
SAMPLE_RANGE_NAME = 'A1:K30'

def Create_Service(client_secret_file, api_service_name, api_version, *scopes):
    global service
    SCOPES = [scope for scope in scopes[0]]
    #print(SCOPES)
    
    cred = None

    if os.path.exists('token_write.pickle'):
        with open('token_write.pickle', 'rb') as token:
            cred = pickle.load(token)

    if not cred or not cred.valid:
        if cred and cred.expired and cred.refresh_token:
            cred.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(client_secret_file, SCOPES)
            cred = flow.run_local_server()

        with open('token_write.pickle', 'wb') as token:
            pickle.dump(cred, token)

    try:
        service = build(api_service_name, api_version, credentials=cred)
        print(api_service_name, 'service created successfully')
        #return service
    except Exception as e:
        print(e)
        #return None
        
# change 'my_json_file.json' by your downloaded JSON file.
Create_Service('my_json_file.json', 'sheets', 'v4',['https://www.googleapis.com/auth/spreadsheets'])
    
def Export_Data_To_Sheets():
    response_date = service.spreadsheets().values().update(
        spreadsheetId=gsheetid,
        valueInputOption='RAW',
        range=SAMPLE_RANGE_NAME,
        body=dict(
            majorDimension='ROWS',
            values=df_gold.T.reset_index().T.values.tolist()) # NB!
    ).execute()
    print('Sheet successfully Updated')

Export_Data_To_Sheets()

