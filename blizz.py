
import sys
import csv
import json
import os

# utilizing local version
sys.path.insert(0, os.path.abspath('../python-blizzardapi'))

from blizzardapi import  BlizzardApi

#from blizzardapi import BlizzardApi
from dotenv import load_dotenv
from requests_oauthlib import OAuth2Session


import pandas as pd
import time
from datetime import datetime
from gsheet import read_spreadsheet, Create_Service, Export_Data_To_Sheets

load_dotenv()


client_id = os.environ.get("CLIENT_ID")
client_secret = os.environ.get("CLIENT_SECRET")
redirect_uri = os.environ.get("REDIRECT_URI")
access_token = os.environ.get("TOKEN")

#kek
import os 
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'


# OAuth endpoints given in the Blizzard API documentation
authorization_base_url =  "https://oauth.battle.net/authorize"
#"https://eu.battle.net/oauth/authorize"
token_url =  "https://oauth.battle.net/token"
#"https://eu.battle.net/oauth/token"

# was wow.proifle
scope = [
    "wow.profile",
]

# getting token: curl -u {client_id}:{client_secret} -d grant_type=client_credentials https://oauth.battle.net/token
# https://eu.battle.net/oauth/token


blizzard = OAuth2Session(client_id, scope=scope, redirect_uri=redirect_uri)

# Redirect user to blizzard for authorization
authorization_url, state = blizzard.authorization_url(authorization_base_url,
    # offline for refresh token
    # force to always make user click authorize
    access_type='offline', prompt='select_account')

print('Please go here and authorize,', authorization_url)

# Get the authorization verifier code from the callback url
redirect_response = input('Paste the full redirect URL here:')


print("REsp.::\n",redirect_response,"\n")

# Fetch the access token
blizzard.fetch_token(token_url, client_secret=client_secret,
    authorization_response=redirect_response)



# Fetch a protected resource, i.e. user profile
# https://eu.api.blizzard.com/profile/user/wow?namespace=profile-us&locale=en_GB&access_token=ABC

r = blizzard.get('https://eu.api.blizzard.com/profile/user/wow?namespace=profile-eu&locale=en_US')

print("API result:", r.status_code)

# process characters

charinfo = json.loads(r.content)

#print(charinfo["_links"])
#print("wowaccounts---->\n")
#print(charinfo["wow_accounts"])

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


#print("Allmychars\n\n")
#print(allmychars)
# ------------------------------------
# Process each character
# ------------------------------------

datarows = []


# get max xp per level
X = pd.read_csv('xp.txt', sep="\t", header=0, usecols=[0,1])


#print("------Chars-----")
#print(charnames)
#print("-----Realms-----")
#print(realmnames)
#print("----------------")


blizapiclient = BlizzardApi(client_id, client_secret)

# cdx = blizapiclient.wow.profile.get_character_profile_summary("eu","en_GB",realm,char)
# print(cdx)

ind = 0


numofchars = len(charnames)

testuri= "https://eu.api.blizzard.com/profile/wow/character/daggerspine/visu?namespace=profile-eu&locale=en_US"
r3 = blizzard.get(testuri)
print("API result:", r3.status_code)
alles = json.loads(r3.content)

print(alles)

# process characters

charinfo = json.loads(r.content)



while ind < numofchars:

    charname = charnames[ind]
    #print("Processing url " + charurl+'&locale=en_US&access_token='+access_token)

    print('\n>>Processing {0} from realm {1}'.format(charname, realmnames[ind]))

    #chardetails = blizapiclient.wow.profile.get_character_profile_summary(
    #    "eu", "en_US", realmnames[ind], charname)

    testuri= "https://eu.api.blizzard.com/profile/wow/character/{0}/{1}?namespace=profile-eu&locale=en_US".format(realmnames[ind],charname)
    r3 = blizzard.get(testuri)
    print("API result:", r3.status_code)
    chardetails = json.loads(r3.content)


    # json.loads(r2.content)
    ind += 1
#   time.sleep(2)

    dataerror = 0

    #print(chardetails)
    if 'achievement_points' in chardetails: 
        achpoints = chardetails['achievement_points']
    else:
        achpoints = "No data"
        dataerror = 1
        chardetails = {'race':{"name":"noRace"}
                       ,'character_class':{'name':'noClass'}
                       ,'realm':{'name':realmnames[ind]}
                       ,'name':charname
                       ,'level':0
                       ,'experience':0.0
                       ,'equipped_item_level':0}

    guildlink = ""
    guilddetails =  None
    guildname = "No guild"


    # guild information
    if 'guild' in chardetails:
        guilddetails = chardetails['guild']

    if guilddetails is not None:
        guildlink = guilddetails['key']['href']
        print("Guild: ", guilddetails['name'] , guildlink, achpoints)
        guildname = guilddetails['name']    


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

    activespec = ""
    if "active_spec" in chardetails:  # for very new chars this does not exist
        #print(chardetails["active_spec"]["name"])
        activespec = chardetails["active_spec"]["name"]
    else:
        activespec = "No spec selected"

    print(chardetails["realm"]["name"])

    renownlvl = 0

    if "covenant_progress" in chardetails:
        renownlvl = chardetails["covenant_progress"]["renown_level"]
        # print(chardetails["covenant_progress"])
    else:
        renownlvl = 0


    if not dataerror:
        level = chardetails["level"]
        totalevel = X["Total"][level]
        levelpros = chardetails["experience"] / totalevel
    else:
        level =0
        totalevel = 0
        levelpros = 0


    print("{0}:Level progress:".format(level), format(levelpros,".4f") , "/", format( levelpros * 100,".2f") , " %")

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
        , guildname
        , achpoints
    ])


# and finally the results processing


header = ["name","character_class","spec","race","realm","level","experience","levelpros","level%", "renown", "ilvl", "Profession1", "Profession1Points","Profession2","Profession2Points", "Guild", "AchPoints" ]

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

#print(df)

print("Sheet reading completed.")

df2 = pd.DataFrame(values_versions[1:], columns=values_versions[0])

indx = len(values_versions)

dateTimeNow = datetime.now()
timestampStr = dateTimeNow.strftime("%d.%m.%Y %H:%M:%S.%f")

new_row = pd.Series(data={'UpdatedDate':timestampStr})
df2 = df2._append(new_row, ignore_index=True)

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

# Fix for mysterious invalid json payload issue, from  
# https://github.com/burnash/gspread/issues/680#issuecomment-561936295
df_gold.fillna(0.0, inplace=True)

print("Final print to sheet ")
Export_Data_To_Sheets(df_gold, df2)


