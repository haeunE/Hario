import requests
import csv
import json
import datetime
from datetime import datetime
from pytz import timezone
import os
import apps.config

def now_stock(code):
    print(code)
    now = datetime.now(timezone('Asia/Seoul'))

    # CSV 파일 저장 경로
    output_file = 'apps/graph/static/cj_stocks_live.csv'

    # CJ 계열사 종목 코드
    cj_stocks = {
        "051500": "CJ프레시웨이",
        "097950": "CJ제일제당",
        "253450": "스튜디오드래곤",
        "311690": "CJ바이오사이언스",
        "000120": "CJ대한통운",
        "011150": "CJ씨푸드",
        "035760": "CJ ENM",
        "079160": "CJ CGV",
        "001040": "CJ(주)"
    }

    # 설정
    price_api_url = 'https://openapi.koreainvestment.com:9443/uapi/domestic-stock/v1/quotations/inquire-time-itemconclusion'
    start_date = '20180101'
    end_date = '20231231'


    headers = {
        'content-type': 'application/json; charset=utf-8',
        'authorization': f'Bearer {apps.config.access_token}',
        'appkey': os.getenv('API_KEY'),
        'appsecret': os.getenv('API_SECRET'),
        'tr_id': 'FHPST01060000'
    }
    if code in cj_stocks.keys():
        # CSV 파일 작성
        with open(output_file, mode='w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Stock Name", "Time", "Now", "Contrast", "Per","AskPrice","BidPrice","Strength","Trading","Execution"])
            stock_code = code
            stock_name = cj_stocks[stock_code]
            print(f"Fetching data for {stock_name} ({stock_code})...")
            params = {
                'FID_COND_MRKT_DIV_CODE': 'J',
                'FID_INPUT_ISCD': stock_code,
                'FID_INPUT_HOUR_1': f"{now.hour:02}{now.minute:02}{(now.second-1):02}"
            }

            for attempt in range(3):  # 최대 3번 재시도
                try:
                    response = requests.get(price_api_url, headers=headers, params=params, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        if 'output2' in data and data['output2']:
                            for entry in data['output2']:
                                try:
                                    time = entry['stck_cntg_hour'] # 주식 체결 시간
                                    current_price = entry['stck_prpr'] # 주식 현재가	
                                    comparison = entry['prdy_vrss'] # 전일 대비
                                    pre_comparison_ratio = entry['prdy_ctrt'] # 전일 대비율
                                    ask_price = entry['askp'] # 매도호가	
                                    bid_price = entry['bidp'] # 매수호가	
                                    tightening_strength = entry['tday_rltv'] # 당일 체결강도
                                    cmulative_trading_volume = entry['acml_vol'] # 누적 거래량
                                    execution_amount= entry['cnqn'] # 체결량
                                    writer.writerow([stock_name, time, current_price, comparison, pre_comparison_ratio, ask_price, bid_price, tightening_strength, cmulative_trading_volume, execution_amount])
                                except KeyError as e:
                                    print(f"Missing key {e} in data entry: {entry}")
                        else:
                            print(f"No valid data for {stock_name} in range {start_date} to {end_date}.")
                        break
                    else:
                        print(f"HTTP Error {response.status_code} for {stock_name} ({start_date} ~ {end_date}): {response.reason}")
                except requests.exceptions.RequestException as e:
                    print(f"Attempt {attempt + 1} failed for {stock_name}: {e}")
            else:
                print(f"Failed to fetch data for {stock_name} from {start_date} to {end_date} after 3 attempts.")
        print(f"Stock data saved to {output_file}.")
    else:
        print("잘못된 접근입니다.")