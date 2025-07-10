import logging
import os
import random
import json
import requests
import redis

from azure.functions import TimerRequest
from datetime import datetime, timezone
MIN_LAT = 37.5020
MAX_LAT = 37.5090
MIN_LON = 127.0950
MAX_LON = 127.1060

# 시뮬레이션할 로봇 개수
NUM_ROBOTS = 2

# 로봇 상태 정의
ROBOT_STATUSES = ["WORKING", "MOVING", "INREST","OFF"]

# Redis 클라이언트 초기화 (환경 변수에서 연결 정보 로드)
REDIS_HOST = os.environ.get("REDIS_HOST")
REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD")
REDIS_PORT = os.environ.get("REDIS_PORT", 6380) # 기본 Redis SSL 포트
REDIS_SSL = os.environ.get("REDIS_SSL", "true").lower() == "true" # SSL 사용 여부

redis_client = None
if REDIS_HOST and REDIS_PASSWORD:
    try:
        redis_client = redis.StrictRedis(
            host=REDIS_HOST,
            port=int(REDIS_PORT),
            password=REDIS_PASSWORD,
            ssl=REDIS_SSL,
            decode_responses=True # 응답을 문자열로 디코딩
        )
        redis_client.ping() # 연결 테스트
        logging.info("Successfully connected to Redis.")
    except Exception as e:
        logging.error(f"Failed to connect to Redis: {e}")
else:
    logging.warning("Redis connection details not found in environment variables. Simulator will not push to Redis.")


def main(mytimer: TimerRequest):
    utc_timestamp = datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()
    logging.info('Robot simulator function started at: %s', utc_timestamp)

    robot_api_url = os.environ.get("ROBOT_API_URL")
    #apim_subscription_key = os.environ.get("APIM_SUBSCRIPTION_KEY")

    if not redis_client:
        logging.error("Redis client not initialized. Skipping data push.")
        return


    for i in range(NUM_ROBOTS):
        
        robotid = f"aw-robot-{i + 1:02d}"  # robot-01, robot-02

        # 랜덤 위치 생성 (소수점 6자리로 포맷)
        latitude = round(MIN_LAT + (MAX_LAT - MIN_LAT) * random.random(), 6)
        longitude = round(MIN_LON + (MAX_LON - MIN_LON) * random.random(), 6)

        # 랜덤 상태 선택
        status = ROBOT_STATUSES[0]

        # JSON 메시지 생성
        robot_data = {
            "botId": robotid,
            "location": str(latitude)+","+ str(longitude), # 문자열로 변환하여 전송
            "botName": robotid,
            "status": status,
            "locationCooSys":"GCS;WGS84",
            "lastUpdated": datetime.now().isoformat() # 현재 시간 (ISO 8601 형식)
        }
        
        json_data = json.dumps(robot_data)

        try:
            logging.info("Sending data for %s: %s", robotid, json_data)
            
            redis_client.set(f"robot:{robotid}:status", json_data)


        except requests.exceptions.RequestException as e:
            logging.error("Error sending data for %s: %s", robotid, e)
        except Exception as e:
            logging.error("An unexpected error occurred for %s: %s", robotid, e)

    logging.info('Robot simulator function finished.')
    

                 
    