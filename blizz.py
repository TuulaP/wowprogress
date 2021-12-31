
from blizzardapi import BlizzardApi
from dotenv import load_dotenv
from requests_oauthlib import OAuth2Session

import csv
import json
import os

import pandas as pd
import time
from datetime import datetime
from gsheet import read_spreadsheet, Create_Service, Export_Data_To_Sheets

load_dotenv()


client_id = os.environ.get("CLIENT_ID")
client_secret = os.environ.get("CLIENT_SECRET")
redirect_uri = os.environ.get("REDIRECT_URI")
access_token = os.environ.get("TOKEN")


# OAuth endpoints given in the Blizzard API documentation
authorization_base_url = "https://eu.battle.net/oauth/authorize"
token_url = "https://eu.battle.net/oauth/token"
scope = [
    "wow.profile",
]

# getting token: curl -u {client_id}:{client_secret} -d grant_type=client_credentials https://eu.battle.net/oauth/token


blizzard = OAuth2Session(client_id, scope=scope, redirect_uri=redirect_uri)

# Redirect user to blizzard for authorization
authorization_url, state = blizzard.authorization_url(authorization_base_url,
    # offline for refresh token
    # force to always make user click authorize
    access_type='offline', prompt='select_account')

print('Please go here and authorize,', authorization_url)

# Get the authorization verifier code from the callback url
redirect_response = input('Paste the full redirect URL here:')

# Fetch the access token
blizzard.fetch_token(token_url, client_secret=client_secret,
    authorization_response=redirect_response)



# Fetch a protected resource, i.e. user profile
# https://eu.api.blizzard.com/profile/user/wow?namespace=profile-us&locale=en_GB&access_token=ABC

r = blizzard.get('https://eu.api.blizzard.com/profile/user/wow?namespace=profile-eu&locale=en_GB')


# process characters

charinfo = json.loads(r.content)

# print(charinfo["_links"])
# print("wowaccounts---->\n")
# print(charinfo["wow_accounts"])

allmychars = []
charnames = []
realmnames = []

for account in charinfo["wow_accounts"]:
    # print("---- ACCCOUNT ----")


    for char in account["characters"]:
        # print("---- CHAR ---- \n")
        # print(char['character'])
        # print(char['name'])
        # print(char['realm']['name'])
        # print(char['playable_class']['name'])

        allmychars.append(char['character']['href'])
        charnames.append(char['name'].lower())

        realmname = char['realm']['name'].lower().replace("-","")
        realmname = realmname.replace(" ","-")
        realmnames.append(realmname)


# print("Allmychars\n\n")
print(allmychars)
# ------------------------------------
# Process each character
# ------------------------------------

datarows = []


# get max xp per level
X = pd.read_csv('xp.txt', sep="\t", header=0, usecols=[0,1])


print(charnames)
print(realmnames)
print("----------------")


blizapiclient = BlizzardApi(client_id, client_secret)

# cdx = blizapiclient.wow.profile.get_character_profile_summary("eu","en_GB",realm,char)
# print(cdx)

ind = 0


numofchars = len(charnames)

while ind < numofchars:

    charname = charnames[ind]
    # print("Processing url ", charurl+'&locale=en_US&access_token='+access_token'

    # r2 = blizzard.get(charurl+'&locale=en_US')
    # print(r2.content)

    print('Processing {0} from realm {1}'.format(charname, realmnames[ind]))

    chardetails = blizapiclient.wow.profile.get_character_profile_summary(
        "eu", "en_GB", realmnames[ind], charname)

    # json.loads(r2.content)
    ind += 1
#    time.sleep(2)

    print(chardetails)

    import sys

    if 'code' in chardetails:
        print('Oh noes! For {0} from {1} realm got '.format(charname, realmnames[ind]), chardetails['code'])
        continue


    # Get character professions, and skill level
    charprofs = {}
    if 'professions' in chardetails:
        ##print("Profs at:", chardetails['professions']['href'])

        r2 = blizzard.get(chardetails['professions']['href'])
        profs = json.loads(r2.content)
        ##print(profs)

        if 'primaries' in profs:
            primaries = profs['primaries']

            for profession in primaries:
                # print("XXX\nXXX\nProfession:", profession)

                if 'tiers' in profession:
                    basedata = profession['tiers'][0]
                    nameofprof = basedata['tier']['name']
                    skillevel = basedata['skill_points']
                    charprofs[nameofprof]=skillevel


    ## print("Professions:", charprofs)



    print(chardetails["name"])
    print(chardetails["race"]["name"])
    print(chardetails["character_class"]["name"])

    activespec = ""
    if "active_spec" in chardetails:  # for very new chars this does not exist
        print(chardetails["active_spec"]["name"])
        activespec = chardetails["active_spec"]["name"]
    else:
        activespec = "No spec selected"

    print(chardetails["realm"]["name"])
    print(chardetails["level"])
    print(chardetails["experience"])


    renownlvl = 0

    if "covenant_progress" in chardetails:
        renownlvl = chardetails["covenant_progress"]["renown_level"]
        # print(chardetails["covenant_progress"])
    else:
        renownlvl = 0


    level = chardetails["level"]
    totalevel = X["Total"][level]
    levelpros = chardetails["experience"] / totalevel

    print("Level progress:", format(levelpros,".4f") , "/", format( levelpros * 100,".2f") , " %")

    career1 = "None1"
    career2 = "None2"
    careerpoints=0
    careerpoints2=0

    for prof in charprofs:
        if career1 == "None1":
            career1 = prof
            careerpoints = charprofs[prof]
        else:
            career2 = prof
            careerpoints2 = charprofs[prof]


    datarows.append([chardetails["name"]
        , chardetails["character_class"]["name"]
        , activespec
        , chardetails["race"]["name"]
        , chardetails["realm"]["name"]
        , chardetails["level"]
        , chardetails["experience"]
        , format(levelpros , ".4f")
        , format(levelpros * 100 , ".2f")
        , renownlvl
        , chardetails['equipped_item_level']
        , career1, careerpoints
        , career2, careerpoints2
    ])



# and finally the results processing


header = ["name","character_class","spec","race","realm","level","experience","levelpros","level%", "renown", "ilvl", "Profession1", "Profession1Points","Profession2","Profession2Points"]

with open('test.csv', 'w', encoding="UTF8") as fp:
    writer = csv.writer(fp, delimiter=',')
    writer.writerow(header)
    writer.writerows(datarows)


# update the google sheet.


print("Login to sheet!")
(values_input, values_versions) = read_spreadsheet()

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

if df_gold['levels_up'].any() < 0:
    df_gold['levels_up'] = pd.to_numeric(df_old['level'])


# fixing up exp counting if leveled up
if df_gold['levels_up'].any() > 0:
    df_gold['exp_diff'] = pd.to_numeric(df['experience'])

# test print
# print(df_gold)


print("Opening sheet")
Create_Service('my_json_file.json', 'sheets', 'v4',['https://www.googleapis.com/auth/spreadsheets'])

# Fix for mysterious invalid json payload issue, from  https://github.com/burnash/gspread/issues/680#issuecomment-561936295
df_gold.fillna('', inplace=True)

print("Final print to sheet ")
Export_Data_To_Sheets(df_gold, df2)


