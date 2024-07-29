import requests
import json
from urllib import parse
import datetime
from config import RIOT_API_KEY
import pandas as pd
import time

BASE_URLS = {
    'kr': 'https://kr.api.riotgames.com',
    'asia': 'https://asia.api.riotgames.com'
}

REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept-Charset": "application/x-www-form-urlencoded; charset=UTF-8",
    "Origin": "https://developer.riotgames.com",
    "X-Riot-Token": RIOT_API_KEY
}

def unix2date(unix):
    return datetime.datetime.fromtimestamp(int(unix))

def get_summoner_puuid(tagLine, gameName, server):
    if(server == 'kr'):
        url = f"{BASE_URLS['asia']}/riot/account/v1/accounts/by-riot-id/{gameName}/{tagLine}"
        response = requests.get(url, headers=REQUEST_HEADERS)
    else:
        print("한국 이외의 서버는 아직 지원하지 않습니다.")

    if response.status_code == 200:
        return response.json()['puuid']  # 소환사 ID 반환
    else:
        print(f"Error fetching summoner ID: {response.status_code}, {response.text}")
        return None

def get_match_lists(summoner_puuid, count, server):
    if(server == 'kr'):
        url = f"{BASE_URLS['asia']}/lol/match/v5/matches/by-puuid/{summoner_puuid}/ids?start=0&count={count}"
        response = requests.get(url, headers=REQUEST_HEADERS)
    else:
        print("한국 이외의 서버는 아직 지원하지 않습니다.")

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching match lists: {response.status_code}, {response.text}")
        return None
    
def get_match_info(match_id, server):
    if(server == 'kr'):
        url = f"{BASE_URLS['asia']}/lol/match/v5/matches/{match_id}"
        response = requests.get(url, headers=REQUEST_HEADERS)
    else:
        print("한국 이외의 서버는 아직 지원하지 않습니다.")

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching match info: {response.status_code}, {response.text}")
        return None
    
def get_nickname_tag(puuid, server):
    if(server == 'kr'):
        url = f"{BASE_URLS['asia']}/riot/account/v1/accounts/by-puuid/{puuid}"
        response = requests.get(url, headers=REQUEST_HEADERS)
    else:
        print("한국 이외의 서버는 아직 지원하지 않습니다.")

    if response.status_code == 200:
        return response.json()
    elif response.status_code == 404:
        print(f"존재하지 않는 회원입니다: {response.status_code}, {response.text}")
        return {
            "gameName": "Unknown",
            "tagLine": "Unknown"
        }
    else:
        print(f"Error fetching nickname and tag: {response.status_code}, {response.text}")
        return None

def run():
    # 플레이어의 닉네임, 서버, 태그 정보 입력
    summoner_name = input('소환사명: ')
    summoner_tag = input('태그: ')
    server = input('서버: ')

    # 소환사 puuid 가져오기
    summoner_puuid = get_summoner_puuid(summoner_tag, summoner_name, server)
    print("puuid: ", summoner_puuid)
    print("============================================================================================================================")

    match_count = input('최근 매치로부터 가져 올 매치의 수(최대 100개): ')
    match_ids = get_match_lists(summoner_puuid, match_count, server)
    print("매치 ID: ", match_ids)
    print("============================================================================================================================")

    result_list = []
    for id in match_ids:
        info = get_match_info(id, server)
        start_time = unix2date(info["info"]["gameCreation"]/1000)
        end_time = unix2date(info["info"]["gameEndTimestamp"]/1000)

        players = []
        for participant_puuid in info["metadata"]["participants"]:
            data = get_nickname_tag(participant_puuid, server)
            time.sleep(1)
            players.append(f"{data['gameName']} #{data['tagLine']}")

        result_list.append({
            "Game": "league of legends",
            "Match ID": id,
            "Start time": start_time,
            "End time": end_time,
            "Nicknames": ", ".join(players)
        })

    result_df = pd.DataFrame(result_list)

    return result_df