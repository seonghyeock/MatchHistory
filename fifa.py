import requests
import json
from urllib import parse
import datetime
from config import FIFA_API_KEY
import time
import pandas as pd

headers = {
    "x-nxopen-api-key": FIFA_API_KEY
}

def get_ouid(nickname):
    url = f"https://open.api.nexon.com/fconline/v1/id?nickname={parse.quote(nickname)}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching ouid: {response.status_code}, {response.text}")
        return None
    
def get_matchtype_metadata():
    url = f"https://open.api.nexon.com/static/fconline/meta/matchtype.json"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching matchtype metadata: {response.status_code}, {response.text}")
        return None
    
def get_match_history(ouid, matchtype, offset, limit):
    url = f"https://open.api.nexon.com/fconline/v1/user/match?ouid={ouid}&matchtype={matchtype}&offset={offset}&limit={limit}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching match history: {response.status_code}, {response.text}")
        return None
    
def get_match_detail(matchId):
    url = f"https://open.api.nexon.com/fconline/v1/match-detail?matchid={matchId}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching match detail: {response.status_code}, {response.text}")
        return None

def run():
    nickname = input("닉네임: ")
    ouid = get_ouid(nickname)['ouid']
    print("ouid: ", ouid)
    print("============================================================================================================================")

    # 전체 matchId 저장
    match_list = []
    for metadata in get_matchtype_metadata():
        match_history = get_match_history(ouid, metadata['matchtype'], 0, 100)
        match_list.append(match_history)
        print(f"{metadata['desc']} matchId: {match_history}")
    print("============================================================================================================================")

    result_list = []
    for match in match_list:
        for matchId in match:
            match_detail = get_match_detail(matchId)
            time.sleep(0.5)

            start_time = datetime.datetime.strptime(match_detail['matchDate'], '%Y-%m-%dT%H:%M:%S')
            end_time = 0

            if(match_detail['matchType'] == 30 or match_detail['matchType'] == 40 or match_detail['matchType'] == 50 or match_detail['matchType'] == 52 or match_detail['matchType'] == 60):
                end_time = start_time + datetime.timedelta(minutes=8)
            else:
                end_time = start_time + datetime.timedelta(minutes=6)

            players = []
            for playerInfo in match_detail['matchInfo']:
                players.append(playerInfo['nickname'])

            result_list.append({
                "Game": "fifa online 4",
                "Match ID": matchId,
                "Start time": start_time,
                "End time": end_time,
                "Nicknames": ", ".join(players)
            })

    result_df = pd.DataFrame(result_list)
    return result_df