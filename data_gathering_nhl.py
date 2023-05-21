# Here is the url for the NHL API resources
# https://github.com/dword4/nhlapi#game-ids

# This script is going to be used to extract data from the NHL API and convert it into a csv file for R Studio to use.


import requests
import json
import pandas as pd
import csv


URL_FOR_GAME_DATA_GATHERING = "https://statsapi.web.nhl.com/api/v1/schedule?startDate=2021-08-01&endDate=2022-08-01&?expand=schedule.linescore"

# DICT ATTRIBUTES
DATES = "dates"
GAMES = "games"
GAME_ID = "gamePk"
GAME_DATE = "date"
GAME_TYPE = "gameType"



# FILE LOCATIONS
GAME_DATA_CSV = "outputs/game_data.csv"

class HockeyGame:
    def __init__(self, gameID, gameDate, homeTeam, awayTeam, homeScore, awayScore, totalScore, winningTeam, losingTeam, gameType):
        self.gameID = gameID
        self.gameDate = gameDate 
        self.homeTeam =homeTeam
        self.awayTeam =  awayTeam
        self.homeScore =  homeScore
        self.awayScore =  awayScore
        self.totalScore =  totalScore
        self.winningTeam =  winningTeam
        self.losingTeam =  losingTeam
        self.gameType = gameType

def get_game_score_data():
    gameList = []
    #This will be where we gather all the game score data from the NHL API
    try:
        result = requests.get(URL_FOR_GAME_DATA_GATHERING)
    except:
        # Request failed
        print(f"Get response failed!")
        exit()
    # Request was successful
    print("Get request was successful. Loading data into json object")
    request_json = json.loads(result.content)
    for date in request_json[DATES]:
        gameDate = date[GAME_DATE]
        for game in date[GAMES]:
            gameID = game[GAME_ID]
            homeTeam = game["teams"]["home"]["team"]["name"]
            awayTeam = game["teams"]["away"]["team"]["name"]
            homeScore = game["teams"]["home"]["score"]
            awayScore = game["teams"]["away"]["score"]
            totalScore = homeScore + awayScore
            if homeScore > awayScore:
                winningTeam = homeTeam
                losingTeam = awayTeam
            else:
                winningTeam = awayTeam
                losingTeam = homeTeam
            gameType = game[GAME_TYPE]
            gameList.append(HockeyGame(gameID, gameDate, homeTeam, awayTeam, homeScore, awayScore, totalScore, winningTeam, losingTeam, gameType))
    gameDataFrame = pd.DataFrame([game.__dict__ for game in gameList])
    gameDataFrame.to_csv(GAME_DATA_CSV, index=False)

        



get_game_score_data()
