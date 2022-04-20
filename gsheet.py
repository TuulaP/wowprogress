import pandas as pd
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow,Flow
from google.auth.transport.requests import Request
import os
import pickle
from datetime import datetime, timedelta

# from https://medium.com/analytics-vidhya/how-to-read-and-write-data-to-google-spreadsheet-using-python-ebf54d51a72c


# here enter the id of your google sheet
from dotenv import load_dotenv


def read_spreadsheet():
    global values_input, service, values_versions

    load_dotenv()  
    gsheetid = os.environ.get("GSHEET_ID")

    SAMPLE_SPREADSHEET_ID_input = gsheetid
    SAMPLE_RANGE_NAME = 'test!A1:U35'  #, was R35, was M30  increase when adding ddata
    RANGE2 = 'versions!A1:A100'
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

    creds = None    

    # better to refresh token every time
    if is_file_older_than('token.pickle', timedelta(hours=12)):
        # remove file
        print("Removing tokens")
        os.remove('token.pickle')
        os.remove('token_write.pickle')



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

    result_input2 = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID_input,
                        range=RANGE2).execute()
    values_versions = result_input2.get('values', [])
    print(values_versions)


    if not values_input and not values_expansion:
        print('No data found.')

    return (values_input, values_versions)




def is_file_older_than (file, delta): 
    # https://stackoverflow.com/a/65412797/364931
    cutoff = datetime.utcnow() - delta
    mtime = datetime.utcfromtimestamp(os.path.getmtime(file))
    if mtime < cutoff:
        return True
    return False



def Create_Service(client_secret_file, api_service_name, api_version, *scopes):
    global service
    SCOPES = [scope for scope in scopes[0]]
    #print(SCOPES)
    
    cred = None

    # better to refresh token every time
    if is_file_older_than('token.pickle', timedelta(hours=12)):
        # remove file
        print("Removing tokens")
        os.remove('token.pickle')
        os.remove('token_write.pickle')
    

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
        
    
def Export_Data_To_Sheets(df_gold, df2):

    load_dotenv()  
    gsheetid = os.environ.get("GSHEET_ID")

    SAMPLE_SPREADSHEET_ID_input = gsheetid
    SAMPLE_RANGE_NAME = 'test!A1:U35'  #, was R35, was M30
    RANGE2 = 'versions!A1:A100'


    response_date = service.spreadsheets().values().update(
        spreadsheetId=gsheetid,
        valueInputOption='RAW',
        range=SAMPLE_RANGE_NAME,
        body=dict(
            majorDimension='ROWS',
            values=df_gold.T.reset_index().T.values.tolist()) # NB!
    ).execute()
    print('Sheet 1 successfully Updated')

    response_data2 = service.spreadsheets().values().update(
        spreadsheetId=gsheetid,
        valueInputOption='RAW',
        range=RANGE2,
        body=dict(
            majorDimension='ROWS',
            values=df2.T.reset_index().T.values.tolist()) # NB!
    ).execute()
    print('Sheet 2 successfully Updated')




if __name__ == '__main__':
    read_spreadsheet()

    ## current values
    df_old = pd.DataFrame(values_input[1:], columns=values_input[0])

    df = pd.read_csv('test.csv')

    print(df)

    print("READING DONE")

    df2 = pd.DataFrame(values_versions[1:], columns=values_versions[0])

    indx = len(values_versions)

    dateTimeNow = datetime.now()
    timestampStr = dateTimeNow.strftime("%d.%m.%Y %H:%M:%S.%f")

    new_row = pd.Series(data={'UpdatedDate':timestampStr})
    df2 = df2.append(new_row, ignore_index=True)

    # df_gold is the new dataframe
    df_gold  = df  # do any processing desired to sheet 1.

    df_gold['exp_diff'] = pd.to_numeric(df['experience']) - pd.to_numeric(df_old['experience'])

    df_gold['levels_up'] = pd.to_numeric(df['level']) - pd.to_numeric(df_old['level'])


    print(df_gold)

    # Filterings
    # df_gold=df[(df['level']=='60')] # & (df['Sport']=='Gymnastics')]


    # change 'my_json_file.json' by your downloaded JSON file.
    Create_Service('my_json_file.json', 'sheets', 'v4',['https://www.googleapis.com/auth/spreadsheets'])

    Export_Data_To_Sheets(df_gold, df2)
