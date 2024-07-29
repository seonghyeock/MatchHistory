import requests
import json
from urllib import parse
import datetime
from config import RIOT_API_KEY

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
    else:
        print(f"Error fetching nickname and tag: {response.status_code}, {response.text}")
        return None

# 플레이어의 닉네임, 서버, 태그 정보 입력
summoner_name = input('소환사명: ')
summoner_tag = input('태그: ')
server = input('서버: ')

# 소환사 puuid 가져오기
summoner_puuid = get_summoner_puuid(summoner_tag, summoner_name, server)
print("puuid: ", summoner_puuid)
print("============================================================================================================================")

match_count = input('최근 매치로부터 가져 올 매치의 수: ')
match_ids = get_match_lists(summoner_puuid, match_count, server)
print("매치 ID: ", match_ids)
print("============================================================================================================================")

for id in match_ids:
    print("매치 ID: ", id)
    info = get_match_info(id, server)
    print("게임 시작 시간: ", unix2date(info["info"]["gameCreation"]/1000))
    print("게임 종료 시간: ", unix2date(info["info"]["gameEndTimestamp"]/1000))

    for participant_puuid in info["metadata"]["participants"]:
        data = get_nickname_tag(participant_puuid, server)
        print(f"플레이어: {data['gameName']} #{data['tagLine']}")

    print("----------------------------------------------------------------------------------------------------------------------------")
