# Here is the url for the NHL API resources
# https://github.com/dword4/nhlapi#game-ids

# This script is going to be used to extract data from the NHL API and convert it into a csv file for R Studio to use.


import requests
import json
import pandas
import csv


URL_FOR_GAME_DATA_GATHERING = "https://statsapi.web.nhl.com/api/v1/schedule?startDate=2022-06-01&endDate=2023-06-01&?expand=schedule.linescore"
VALID = "<Response [200]>"

def get_game_score_data():
    #This will be where we gather all the game score data from the NHL API
    result = requests.get(URL_FOR_GAME_DATA_GATHERING)
    print(result)
    if result is VALID:
        request_json = json.loads(result.content)
        print("We did it")


get_game_score_data()
print("hello")