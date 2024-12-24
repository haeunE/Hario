import os
import requests
from datetime import datetime, timedelta
import apps.config
import time
import json

def get_new_token(): 
  TOKEN_URL = 'https://openapi.koreainvestment.com:9443/oauth2/tokenP'
#   global access_token
  headers = {
      "Content-type": "application/json; charset=UTF-8"
  }

  # 토큰 요청 데이터
  data = {
    "grant_type": "client_credentials",
    "appkey": os.getenv('API_KEY'),
    "appsecret":  os.getenv('API_SECRET')
  }
  # 토큰 요청
  response = requests.post(TOKEN_URL, headers=headers, json=data)

  # 응답 처리
  if response.status_code == 200:
      token_data = response.json()
      apps.config.access_token = token_data.get('access_token')
      expires_in = token_data.get('expires_in')
      print(f"Access Token: {apps.config.access_token}")
      print(f"Token Expires In: {expires_in} seconds")
  else:
      print(f"Error: {response.status_code}, {response.text}")
      
def get_access_token():

  # 토큰이 없거나 만료된 경우 새로 발급
  if apps.config.access_token is None:
      print("Generating a new token...")
      get_new_token()
  else:
      print("Using existing token...")
  return apps.config.access_token

# 웹소켓 접속키 발급
def get_approval():
    if apps.config.approval_key is None:
        print("Generating a new key...")
        # url = https://openapivts.koreainvestment.com:29443' # 모의투자계좌     
        url = 'https://openapi.koreainvestment.com:9443' # 실전투자계좌
        headers = {"content-type": "application/json"}
        body = {"grant_type": "client_credentials",
                "appkey": os.getenv('API_KEY'),
                "secretkey": os.getenv('API_SECRET')}
        PATH = "oauth2/Approval"
        URL = f"{url}/{PATH}"
        time.sleep(0.05)
        res = requests.post(URL, headers=headers, data=json.dumps(body))
        apps.config.approval_key = res.json()["approval_key"]
        return apps.config.approval_key