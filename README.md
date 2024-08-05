# wowprogress

Attempt to get blizzard character data for excel  (idea to follow the leveling progress of multiple alts) :)


Basic flow:


_blizz.py_

- login to blizzard api and get characters of an account  (oauthlib)
     - create dev account and then app to [get client_id and secret](https://develop.battle.net/documentation/guides/using-oauth) (store those to .env file)   
     - developer portal at: https://develop.battle.net/access/clients ('API access') on toolbar.
     - SELFNOTE: use chrome as default browser 
 - Script gives an url to command line, and after putting it to the browser, you get the return uri which is given back to script
     - return_uri must be in app settings in blizzard site
     - return uri could be e.g. the [blizzard-api-proxy](https://github.com/francis-schiavo/blizzard-api-proxy) deployed to heroku 
     - return uri actually does not even need to be running, it is enough for this script just to copy the "proposed" url for everything to work.
     (not very convenient, but simple enough)
     
- Script goes through each character of account and gets character data via summary api (blizzardapi)

- Script gets interesting data about character level and calculate progress towards next level
    - max level data from [wow.tools](https://wow.tools/files/#search=gametables%2Fxp.txt&page=1&sort=0&desc=asc) (obtained 30.10.2021)
    
- Store character data to a table, which is then written to "test.csv" csv file.
- The csv file is then stored to a google sheet.
- NB! If google sheet login fails, remove the token.pickle and token_write.pickle. Then there occurs
reauthentication and files get recreated.


test.csv output sample
<pre>
name,character_class,spec,race,realm,level,experience,levelpros,level%,renown,ilvl,prof1,prof1points,prof2,prof2points
Somefancycharactername,Warlock,Destruction,race1,Somerealm,24,24824,0.8902,89.02,0,26,Pandaria Alchemy, 25
Anotherawesomecharacter,Shaman,Restoration,race2,Realmtoo,60,0,0.0000,0.00,80,246,Zandalari Engineering, 35
</pre>




**Todo**

- prettify & refactor
- renowns of Shadowlands (4 areas, what is renown level in each)
- "what has changed" since last run info (new column(s)), background color to sheet?
     * ~~e.g. exp gone up by X points.~~
     * character Z has gone up Y levels -> BUG: sometimes level difference goes negative(???)
- Is it possible to follow-up currencies, which character has which amount of Champion's Seals etc.?
- 




