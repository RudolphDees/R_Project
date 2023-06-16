# Here is the url for the NHL API resources
# https://github.com/dword4/nhlapi#game-ids

# This script is going to be used to extract data from the NHL API and convert it into a csv file for R Studio to use.


import requests
import json
import pandas as pd
import csv
from pathlib import Path
from datetime import datetime

# This is the url for gathering game play data: https://statsapi.web.nhl.com/api/v1/game/ID/feed/live
URL_FOR_GAME_DATA_GATHERING = "https://statsapi.web.nhl.com/api/v1/schedule?startDate=2018-10-01&endDate=2022-10-10&?expand=schedule.linescore"

# DICT ATTRIBUTES
DATES = "dates"
GAMES = "games"
GAME_ID = "gamePk"
DATE = "date"
GAME_TYPE = "gameType"
TOTAL_SCORE = "totalScore"
AWAY_SCORE = "awayScore"
HOME_SCORE = "homeScore"
WINNING_TEAM = "winningTeam"
LOSING_TEAM = "losingTeam"
HOME_TEAM = "homeTeam"
AWAY_TEAM = "awayTeam"
GAME_DATE = "gameDate"





# FILE LOCATIONS
GAME_DATA_CSV = "./outputs/game_data.csv"
PLAY_DATA_CSV = "./outputs/play_data.csv"
DATE_SUMMARY_DATA_CSV = "./outputs/date_summary_data.csv"

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

class dateSummary:
    def __init__(self, date, dayOfTheWeek, avgTotalScore, avgHomeScore, avgAwayScore, numberOfGames, avgHomeWins, avgAwayWins):
        self.date = date
        self.dayOfTheWeek = dayOfTheWeek
        self.avgTotalScore = avgTotalScore
        self.avgHomeScore =  avgHomeScore
        self.avgAwayScore =  avgAwayScore
        self.numberOfGames =  numberOfGames
        self.avgHomeWins =  avgHomeWins
        self.avgAwayWins = avgAwayWins

class playSummary:
    def __init__(self, play_type, xLoc, yLoc):
        self.play_type = play_type
        self.xLoc = xLoc
        self.yLoc = yLoc
        # self.result = result

    
        
def get_game_play_data(game_id, play_list):
    """
    This function extracts data from the NHL API for every play that happens in a specific game.
    

    Parameters: Game ID, play_list array
    """
    api_url = f'https://statsapi.web.nhl.com/api/v1/game/{game_id}/feed/live'
    try:
        result = requests.get(api_url)
    except:
        # Request failed
        print(f"Get response failed in get_game_play_data!")
        return
    # Request was successful
    request_json = json.loads(result.content)
    for play in request_json["liveData"]["plays"]["allPlays"]:
        if play["result"]["event"] == "Shot" or play["result"]["event"] == "Goal":
            if "secondaryType" in play["result"]:
                shot_type = play["result"]["secondaryType"]
                if "coordinates" in play:
                    if "x" in play["coordinates"]:
                        xLoc = float(play["coordinates"]["x"])
                else:
                    continue
                if "coordinates" in play:
                    if "y" in play["coordinates"]:
                        yLoc = float(play["coordinates"]["y"])
                else:
                    continue
                if play["result"]["event"] == "Goal":
                    play_result = 1
                else:
                    play_result = 0
                play_list.append(playSummary(xLoc, yLoc, play_result))
            else:
                # This play does not have a secondaryType for some reason
                pass
        else:
            # This was not a shot so we don't care what happened for now
            pass
    return play_list
    


def get_game_score_data(gather_play_data):
    """
    This function extracts data from the NHL API for every game from the desired season.
    As of right now the season is hard coded into the URL
    TODO: I need to fix that

    Parameters: gather_play_data bool
    """
    gameList = []
    playData = []
    #This will be where we gather all the game score data from the NHL API
    try:
        result = requests.get(URL_FOR_GAME_DATA_GATHERING)
    except:
        # Request failed
        print(f"Get response failed in get_game_score_data!")
        exit()
    # Request was successful
    print("Get request was successful. Loading data into json object")
    request_json = json.loads(result.content)
    for date in request_json[DATES]:
        gameDate = date[DATE]
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
            if gather_play_data:
                playData = get_game_play_data(gameID, playData)


    gameDataFrame = pd.DataFrame([game.__dict__ for game in gameList])
    gameDataFrame.to_csv(GAME_DATA_CSV, index=False)
    if gather_play_data:
        playDataFrame = pd.DataFrame([play.__dict__ for play in playData])
        playDataFrame.to_csv(PLAY_DATA_CSV, index=False)


        
def get_daily_summary_from_game_score_data(gather_play_data):
    """
    This function will take the game data from "./outputs/game_data.csv" and refine it down to just be about each specific day
    It will average out the number of games per day, whether the home or away team won more and so on. This will be much easier to
    work with later on.

    Parameters: gather_play_data bool determines if we will gather the play data or not
     
    It automatically checks if the game data is available. If it is not it will retrieve it automatically.
    """
    # Initializing values
    dateSummaryList = []
    game_data_path = Path(GAME_DATA_CSV)
    date_summary_path = Path(DATE_SUMMARY_DATA_CSV)
    current_date = ''
    avgTotalScore = 0
    avgHomeScore = 0
    avgAwayScore = 0
    numberOfGames = 0
    avgHomeWins = 0
    avgAwayWins = 0
    if game_data_path.is_file() is False:
        print("We do not have game data yet. Getting it now.")
        get_game_score_data(gather_play_data)
    if date_summary_path.is_file() is False:
        with open(GAME_DATA_CSV, 'r') as game_data_file:
            # Opening up the file so we can read it.
            game_data = csv.DictReader(game_data_file, delimiter=',')
            for game in game_data:
                game_date = game[GAME_DATE]
                if current_date == '':
                    # The date has not been initialized so we do that here.
                    current_date == game_date
                elif current_date != game_date:
                    # The date has changed so we create a dateSummary object to store the current data and wipe the values to start fresh.
                    avgTotalScore = avgTotalScore / numberOfGames
                    avgHomeScore = avgHomeScore / numberOfGames
                    avgAwayScore = avgAwayScore / numberOfGames
                    avgHomeWins = avgHomeWins / numberOfGames
                    avgAwayWins = avgAwayWins / numberOfGames

                    current_date_dt = datetime.strptime(current_date, "%Y-%m-%d")
                    dayOfTheWeek = current_date_dt.weekday()
                    dateSummaryList.append(dateSummary(current_date, dayOfTheWeek, avgTotalScore, avgHomeScore, avgAwayScore, numberOfGames, avgHomeWins, avgAwayWins))
                    avgTotalScore = 0
                    avgHomeScore = 0
                    avgAwayScore = 0
                    numberOfGames = 0
                    avgHomeWins = 0
                    avgAwayWins = 0
                current_date = game_date
                avgTotalScore += int(game[TOTAL_SCORE])
                avgHomeScore += int(game[HOME_SCORE])
                avgAwayScore += int(game[AWAY_SCORE])
                numberOfGames += 1
                if game[WINNING_TEAM] == game[HOME_TEAM]:
                    avgHomeWins += 1
                else:
                    avgAwayWins += 1
        gameDataFrame = pd.DataFrame([day.__dict__ for day in dateSummaryList])
        gameDataFrame.to_csv(DATE_SUMMARY_DATA_CSV, index=False)
    else:
        print("The data already exists so we will not be running it again.")
            

    
        

get_daily_summary_from_game_score_data(True)
