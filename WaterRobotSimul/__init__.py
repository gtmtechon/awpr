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


def main(mytimer: TimerRequest):
    robot_api_url = "https://iotmon-comm-be.azurewebsites.net/api/waterbots"

    response = requests.get(robot_api_url)
    print("response:", response)
    logging.info('response: %s', response.text)
    

                 
    