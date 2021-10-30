# wowprogress

Attempt to get blizzard character data for excel


Basic flow:

- login to blizzard api and get characters of an account  (oauthlib)
- go through each character and gets its data via summary api (blizzardapi)
- get interesting data about character level and calculate progress towards next level
    - max level data from https://wow.tools/files/#search=gametables%2Fxp.txt&page=1&sort=0&desc=asc
    
- Store this data as table and then to "test.csv" csv file.


TODO
- move to google sheets, char summary should be doable via token authentication
- prettify
- lint



