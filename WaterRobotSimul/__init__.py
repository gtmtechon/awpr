import logging
import os
import random
import json
import requests

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


#@app.timer_trigger(schedule="*/30 * * * * *", arg_name="myTimer", run_on_startup=False, use_monitor=False) 
def RobotSimulatorFunction(mytimer: TimerRequest):
    utc_timestamp = datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()
    logging.info('Robot simulator function started at: %s', utc_timestamp)

    robot_api_url = os.environ.get("ROBOT_API_URL")
    apim_subscription_key = os.environ.get("APIM_SUBSCRIPTION_KEY")

    if not robot_api_url:
        logging.error("Missing environment variable: ROBOT_API_URL")
        return

    headers = {
        'Content-Type': 'application/json',
    }
    #if apim_subscription_key:
    #    headers['Ocp-Apim-Subscription-Key'] = apim_subscription_key

    for i in range(NUM_ROBOTS):
        robotid = f"robot-{i + 1:02d}"  # robot-01, robot-02

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

        try:
            logging.info("Sending data for %s: %s", robotid, json.dumps(robot_data))
            response = requests.post(robot_api_url, headers=headers, json=robot_data)
            response.raise_for_status() # HTTP 오류 발생 시 예외 발생

            logging.info("Successfully sent data for %s. Status: %d, Response: %s",
                         robotid, response.status_code, response.text)

        except requests.exceptions.RequestException as e:
            logging.error("Error sending data for %s: %s", robotid, e)
        except Exception as e:
            logging.error("An unexpected error occurred for %s: %s", robotid, e)

    logging.info('Robot simulator function finished.')
    


def main(mytimer: TimerRequest) -> None:
    utc_timestamp = datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()
    logging.info('Robot simulator function started at: %s', utc_timestamp)

    robot_api_url = os.environ.get("ROBOT_API_URL")
    #apim_subscription_key = os.environ.get("APIM_SUBSCRIPTION_KEY")

    if not robot_api_url:
        robot_api_url = "https://iotmon-comm-be.azurewebsites.net/api/waterbots"

    headers = {
        'Content-Type': 'application/json',
    }
    #if apim_subscription_key:
    #    headers['Ocp-Apim-Subscription-Key'] = apim_subscription_key

    robotid = "water-robot-001"  # robot-01, robot-02

    # 랜덤 위치 생성 (소수점 6자리로 포맷)
    latitude = round(MIN_LAT + (MAX_LAT - MIN_LAT) * random.random(), 6)
    longitude = round(MIN_LON + (MAX_LON - MIN_LON) * random.random(), 6)

    # 랜덤 상태 선택
    status = "WORKING"

    # JSON 메시지 생성
    robot_data = {
        "botId": robotid,
        "location": str(latitude)+","+ str(longitude), # 문자열로 변환하여 전송
        "botName": robotid,
        "status": status,
        "locationCooSys":"GCS;WGS84",
        "lastUpdated": datetime.now().isoformat() # 현재 시간 (ISO 8601 형식)
    }

    try:
        logging.info("Sending data for %s: %s", robotid, json.dumps(robot_data))
        response = requests.post(robot_api_url, headers=headers, json=robot_data)
        response.raise_for_status() # HTTP 오류 발생 시 예외 발생

        logging.info("Successfully sent data for %s. Status: %d, Response: %s",
                        robotid, response.status_code, response.text)

    except requests.exceptions.RequestException as e:
        logging.error("Error sending data for %s: %s", robotid, e)
    except Exception as e:
        logging.error("An unexpected error occurred for %s: %s", robotid, e)

    logging.info('Robot simulator function finished.')
    