import logging
import os
import random
import json
import redis
from azure.functions import TimerRequest
from datetime import datetime, timezone

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

MIN_LAT = 37.5020
MAX_LAT = 37.5090
MIN_LON = 127.0950
MAX_LON = 127.1060

NUM_ROBOTS = 2
ROBOT_STATUSES = ["WORKING", "MOVING", "INREST", "OFF"]

# Redis 클라이언트 초기화 (환경 변수에서 연결 정보 로드)
REDIS_HOST = os.environ.get("REDIS_HOST")
REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD")
REDIS_PORT = os.environ.get("REDIS_PORT", 6380)
REDIS_SSL = os.environ.get("REDIS_SSL", "true").lower() == "true"

redis_client = None
if REDIS_HOST and REDIS_PASSWORD:
    try:
        redis_client = redis.StrictRedis(
            host=REDIS_HOST,
            port=int(REDIS_PORT),
            password=REDIS_PASSWORD,
            ssl=REDIS_SSL,
            decode_responses=True
        )
        redis_client.ping()
        logging.info("Successfully connected to Redis.")
    except Exception as e:
        logging.error(f"Failed to connect to Redis: {e}")
else:
    logging.warning("Redis connection details not found in environment variables. Simulator will not push to Redis.")

def main(mytimer: TimerRequest): # mytimer: TimerRequest 인자 제거, Azure Function이 아닌 일반 스크립트로 가정
    utc_timestamp = datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()
    logging.info('Robot simulator function started at: %s', utc_timestamp)

    if not redis_client:
        logging.error("Redis client not initialized. Skipping data push.")
        return

    for i in range(NUM_ROBOTS):
        robotid = f"aw-robot-{i + 1:02d}"

        latitude = round(MIN_LAT + (MAX_LAT - MIN_LAT) * random.random(), 6)
        longitude = round(MIN_LON + (MAX_LON - MIN_LON) * random.random(), 6)
        status = random.choice(ROBOT_STATUSES) # 상태를 랜덤하게 선택

        robot_data = {
            "botId": robotid,
            "location": f"{latitude},{longitude}",
            "botName": robotid,
            "status": status,
            "locationCooSys": "GCS;WGS84",
            "lastUpdated": datetime.now().isoformat()
        }
        
        json_data = json.dumps(robot_data)

        try:
            logging.info("Processing data for %s: %s", robotid, json_data)
            
            # Redis Hash에 로봇의 최신 상태 저장 (HSET)
            # HSET key field value
            redis_client.hset(f"robot:{robotid}", mapping=robot_data)
            logging.info(f"Saved robot:{robotid} to Redis Hash.")

            # Redis Pub/Sub 채널에 메시지 발행 (PUBLISH)
            # PUBLISH channel message
            redis_client.publish("robot_updates", json_data)
            logging.info(f"Published data for {robotid} to 'robot_updates' channel.")

        except redis.exceptions.RedisError as e:
            logging.error("Redis error for %s: %s", robotid, e)
        except Exception as e:
            logging.error("An unexpected error occurred for %s: %s", robotid, e)

    logging.info('Robot simulator function finished.')
