### 모듈 임포트 ###
import os
import sys
import json
import time
import requests
import asyncio
import traceback
import websockets
import apps.config
# from Crypto.Cipher import AES
# from Crypto.Util.Padding import unpad
from base64 import b64decode

from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import unpad

clearConsole = lambda: os.system('cls' if os.name in ('nt', 'dos') else 'clear')

key_bytes = 32


### 함수 정의 ###

# AES256 DECODE
def aes_cbc_base64_dec(key, iv, cipher_text):
    """
    :param key:  str type AES256 secret key value
    :param iv: str type AES256 Initialize Vector
    :param cipher_text: Base64 encoded AES256 str
    :return: Base64-AES256 decodec str
    """
    cipher = AES.new(key.encode('utf-8'), AES.MODE_CBC, iv.encode('utf-8'))
    return bytes.decode(unpad(cipher.decrypt(b64decode(cipher_text)), AES.block_size))


# CJ 계열사 종목 코드
cj_stocks = {
    "CJ제일제당": "097950",
    "스튜디오드래곤": "253450",
    "CJ바이오사이언스": "311690",
    "CJ대한통운": "000120",
    "CJ씨푸드": "011150",
    "CJ ENM": "035760",
    "CJ CGV": "079160",
    "CJ(주)": "001040"
}

# 국내주식체결처리 출력라이브러리
def stockspurchase_domestic(data_cnt, data,name):
    conclu = []  # csv에 넣을 데이터 리스트
    print("============================================")
    print(f'채결수 : {data_cnt}')
    print("============================================")
    menulist = "유가증권단축종목코드|주식체결시간|주식현재가|전일대비부호|전일대비|전일대비율|가중평균주식가격|주식시가|주식최고가|주식최저가|매도호가1|매수호가1|체결거래량|누적거래량|누적거래대금|매도체결건수|매수체결건수|순매수체결건수|체결강도|총매도수량|총매수수량|체결구분|매수비율|전일거래량대비등락율|시가시간|시가대비구분|시가대비|최고가시간|고가대비구분|고가대비|최저가시간|저가대비구분|저가대비|영업일자|신장운영구분코드|거래정지여부|매도호가잔량|매수호가잔량|총매도호가잔량|총매수호가잔량|거래량회전율|전일동시간누적거래량|전일동시간누적거래량비율|시간구분코드|임의종료구분코드|정적VI발동기준가"
    menustr = menulist.split('|')
    pValue = data.split('^')
    i = 0
    for cnt in range(data_cnt):  # 넘겨받은 체결데이터 개수만큼 print 한다
        print("### [%d / %d]" % (cnt + 1, data_cnt))
        conclu.append([name,pValue[1],pValue[2],pValue[4],pValue[5],pValue[10],pValue[11],pValue[18],pValue[13],pValue[12]])
        for menu in menustr:
            print("%-13s[%s]" % (menu, pValue[i]))
            i += 1
    print("conclu" , conclu)
    return conclu


async def connect(stock_name):
  if stock_name in cj_stocks.keys():
    try:
      url = 'ws://ops.koreainvestment.com:21000' # 실전투자계좌

      # 원하는 호출을 [tr_type, tr_id, tr_key] 순서대로 리스트 만들기
      code_list = [['1','H0STCNT0',cj_stocks[stock_name]]]
      senddata_list=[]

      print("url : ", url)
      print(apps.config.approval_key)

      for i,j,k in code_list:
        temp = '{"header":{"approval_key": "%s","custtype":"P","tr_type":"%s","content-type":"utf-8"},"body":{"input":{"tr_id":"%s","tr_key":"%s"}}}'%(apps.config.approval_key,i,j,k)
        senddata_list.append(temp)

      async with websockets.connect(url, ping_interval=None) as websocket:

        for senddata in senddata_list:
          await websocket.send(senddata)
          await asyncio.sleep(0.5)
          print(f"Input Command is :{senddata}")

        while True:
          data = await websocket.recv() # 클라이언트로부터 메시지를 대기한다.
          # await asyncio.sleep(0.5)
          print(f"Recev Command is :{data}")  # 정제되지 않은 Request / Response 출력

          if data[0] == '0':
            recvstr = data.split('|')  # 수신데이터가 실데이터 이전은 '|'로 나뉘어져있어 split
            trid0 = recvstr[1]

            print(f'recvstr{recvstr}')

            if trid0 == "H0STCNT0":  # 주식체결 데이터 처리
              print("#### 국내주식 체결 ####")
              data_cnt = int(recvstr[2])  # 체결데이터 개수
              return stockspurchase_domestic(data_cnt, recvstr[3],stock_name)
              
              # await asyncio.sleep(0.2)

          else:

            jsonObject = json.loads(data)
            trid = jsonObject["header"]["tr_id"]

            if trid == "PINGPONG":
              print("### RECV [PINGPONG] [%s]" % (data))
              await websocket.pong(data)
              print("### SEND [PINGPONG] [%s]" % (data))
    except Exception as e:
      print('Exception Raised!')
      print(e)
      print('Connect Again!')
      time.sleep(0.1)

      # 웹소켓 다시 시작
      await connect()   
  else:
    print("Stock Code Error")