# wowprogress

Attempt to get blizzard character data for excel  (idea to follow the leveling progress of multiple alts) :)


Basic flow:


_blizz.py_

- login to blizzard api and get characters of an account  (oauthlib)
     - create dev account and then app to [get client_id and secret](https://develop.battle.net/documentation/guides/using-oauth) (store those to .env file)   
 - Script gives an url to command line, and after putting it to the browser, you get the return uri which is given back to script
     - return_uri must be in app settings in blizzard site
     - return uri could be e.g. the [blizzard-api-proxy](https://github.com/francis-schiavo/blizzard-api-proxy) deployed to heroku 
- Script goes through each character of account and gets character data via summary api (blizzardapi)
- get interesting data about character level and calculate progress towards next level
    - max level data from [wow.tools](https://wow.tools/files/#search=gametables%2Fxp.txt&page=1&sort=0&desc=asc) (obtained 30.10.2021)
    
- Store character data to a table, which is then written to "test.csv" csv file.


test.csv output sample
<pre>
name,character_class,spec,race,realm,level,experience,levelpros,level%,renown,ilvl
Somefancycharactername,Warlock,Destruction,race1,Somerealm,24,24824,0.8902,89.02,0,26
Anotherawesomecharacter,Shaman,Restoration,race2,Realmtoo,60,0,0.0000,0.00,80,246
</pre>



TODO

- move to google sheets, char summary should be doable via token authentication, probably would just require listing of chars and realms there...
- prettify
- lint



