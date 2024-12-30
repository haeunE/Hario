from flask import Blueprint, render_template
import folium.plugins
import pandas as pd
import matplotlib, io, os, base64, json, folium, chardet
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib import font_manager
matplotlib.use('Agg')

font_path = "C:/Windows/Fonts/malgun.ttf"
font_prop = font_manager.FontProperties(fname=font_path)
plt.rcParams['font.family'] = font_prop.get_name()
plt.rcParams['axes.unicode_minus'] = False  # 마이너스 기호 깨짐 방지

logistics = Blueprint('logistics', __name__, template_folder='templates', static_folder='static')
geojson_path = os.path.join('apps', 'logistics', '서울_자치구_경계_2017.geojson')

csv_files_all = [
    ('apps/logistics/logi_all.csv', '전체 기간 (2018~2024)')
]
csv_files_term = [
    ('apps/logistics/logi_before.csv', '코로나 이전 (2018.01 ~ 2019.12)'),
    ('apps/logistics/logi_during.csv', '코로나 기간 (2020.01 ~ 2022.04)'),
    ('apps/logistics/logi_after.csv', '코로나 이후 (2022.05 ~ 2023.12)')
]

def generate_logi_all():
    column_remove = [    # 제거할 열
        '송하인_시명', '송하인_시코드', '송하인_구명', '송하인_구코드',
        '수하인_시명', '수하인_시코드', '수하인_구명', '수하인_구코드'
    ]

    dfs = []
    for file_path, _ in csv_files_term:
        df = pd.read_csv(file_path, encoding='euc-kr')
        df = df.loc[(df != 0).any(axis=1)]  # 값이 0이 아닌 행만
        dfs.append(df)

    df_all = pd.concat(dfs)
    df_cleaned = df_all.drop(columns=column_remove, errors='ignore') #  # logi_all.csv 파일 생성, 불필요한 열 제거
    date_voiume_sum = df_cleaned.groupby(['배송년월일']).sum()  # 날짜별 운송량 집계
    date_voiume_sum.to_csv('apps/logistics/logi_all.csv', encoding='utf-8-sig')  # 최종 파일로 저장
    
    return date_voiume_sum


@logistics.route('/')
def logistics_page():
    # 'logi_all.csv' 파일 생성 및 전처리
    generate_logi_all()
    
    columns_item = [
    '가구/인테리어', '도서/음반', '디지털/가전', '생활/건강', 
    '스포츠/레저', '식품', '출산/육아', '패션의류', '패션잡화', '화장품/미용'
    ]
    
    pie_item_img, line_item_img, weekday_line_img, columns_item = logistics_graph(csv_files_all, csv_files_term, columns_item)
    bar_item_img = logistics_bar_graph(csv_files_term)
    
    df_all = read_csv('apps/logistics/logi_all.csv')
    total_volume_all = df_all[columns_item].sum()  # 전체 품목별 운송량 합계

    # pie_analysis        
    top_pie_item, top_pie_percent, second_pie_item, second_pie_percent, third_pie_item, third_pie_percent = pie_analysis(total_volume_all)
   
    # bar_analysis        
    high_bar_period, high_bar_volume, low_bar_period, low_bar_volume = bar_analysis(csv_files_term, columns_item)
    
    # map_analysis        
    dual_map, top_sender, top_receiver, combined_text = color_map(csv_files_term, columns_item)
    
    # line_analysis        
    high_month, low_month, monthly_avg_volume = line_analysis(csv_files_term, columns_item)

    # weekday_line_analysis
    weekday_analysis_result = weekday_line_analysis(csv_files_all, columns_item)


    return render_template(
        'logistics/logistics.html', 
        pie_plot_urls=pie_item_img, 
        line_plot_urls=line_item_img, 
        bar_plot_urls=bar_item_img,
        weekday_line_plot_urls=weekday_line_img,
        
        dual_map=dual_map, 
        top_sender=top_sender, 
        top_receiver=top_receiver, 
        combined_text=combined_text,
        
        top_pie_item=top_pie_item,
        top_pie_percent=top_pie_percent,
        second_pie_item=second_pie_item,
        second_pie_percent=second_pie_percent,
        third_pie_item=third_pie_item,
        third_pie_percent=third_pie_percent,
        
        high_bar_period=high_bar_period,
        high_bar_volume=high_bar_volume,
        low_bar_period=low_bar_period,
        low_bar_volume=low_bar_volume,
        
        high_month=high_month,
        low_month=low_month,
        monthly_avg_volume=monthly_avg_volume,
        total_volume_all=total_volume_all,

        high_day=weekday_analysis_result['high_day'],
        high_day_mean=weekday_analysis_result['high_day_mean'],
        low_day=weekday_analysis_result['low_day'],
        low_day_mean=weekday_analysis_result['low_day_mean']
    )


def read_csv(file_path):
    with open(file_path, 'rb') as f:
        encoding = chardet.detect(f.read(1000))['encoding'] # 파일의 첫 1000바이트만 읽어 인코딩 추정
   
    return pd.read_csv(file_path, encoding=encoding) 


def logistics_graph(csv_files_all, csv_files_term, columns_item):
    pie_item_img, line_item_img, weekday_line_img = [], [], []

    # 전체 기간 그래프 생성 (csv_files_all)
    for file_path, title_prefix in csv_files_all:
        bar_item, pie_item, line_item = generate_graph(file_path, title_prefix, columns_item)
        pie_item_img.append(pie_item)
        line_item_img.append(line_item)

    # 코로나 이전, 코로나 기간, 코로나 이후 그래프 생성 (csv_files_term)
    for file_path, title_prefix in csv_files_term:
        bar_item, pie_item, line_item = generate_graph(file_path, title_prefix, columns_item)
        pie_item_img.append(pie_item)
        line_item_img.append(line_item)

    # 전체 기간 요일별 선형 그래프
    weekday_line_img.append(plot_weekday_line_graph('apps/logistics/logi_all.csv', columns_item))
    
    return pie_item_img, line_item_img, weekday_line_img, columns_item

def generate_graph(file_path, title_prefix, columns_item):
    # CSV 파일 읽기
    df = read_csv(file_path)
    df['배송년월일'] = pd.to_datetime(df['배송년월일'], format='%Y%m%d')  # 날짜 형식 변환
    df.set_index('배송년월일', inplace=True)  # 날짜를 인덱스로 설정

    # 각 항목의 총합 계산
    total_volume = df[columns_item].sum()

    # 그래프 생성
    bar_item = plot_bar_graph(title_prefix, columns_item, total_volume)
    pie_item = plot_pie_graph(total_volume, title_prefix)
    line_item = plot_line_graph(df, columns_item, title_prefix)

    return bar_item, pie_item, line_item

# 전체 기간 품목별 파이형 그래프
def plot_pie_graph(data, title):
    sorted_data = data.sort_values(ascending=False)
    colors = plt.cm.Paired(range(len(sorted_data)))
    
    plt.figure(figsize=(6, 6))
    wedges = plt.pie(
        sorted_data, 
        autopct='%1.1f%%', 
        startangle=90, 
        colors=colors, 
        pctdistance=0.8
    )
    
    plt.legend(wedges, sorted_data.index, loc='upper left', bbox_to_anchor=(1, 1), fontsize=10)
    plt.tight_layout()
    # plt.title(f'{title}')

    pie_img_io = io.BytesIO()
    plt.savefig(pie_img_io, format='png')
    pie_img_io.seek(0)
    pie_item_img = base64.b64encode(pie_img_io.getvalue()).decode()
    plt.close()

    return pie_item_img    


def pie_analysis(total_volume):
    total = total_volume.sum()
    sorted_volume = total_volume.sort_values(ascending=False)
    top_items = sorted_volume.iloc[:3]
    top_items_percentage = (top_items / total) * 100

    result = [(top_items.index[i], round(top_items_percentage.iloc[i], 1)) for i in range(3)]

    return tuple(result[0] + result[1] + result[2])


# 코로나 기간 별 운송량 (막대 그래프)
def logistics_bar_graph(csv_files_term):
    columns_item = [
        '가구/인테리어', '도서/음반', '디지털/가전', '생활/건강', 
        '스포츠/레저', '식품', '출산/육아', '패션의류', '패션잡화', '화장품/미용'
    ]
    total_volume = pd.DataFrame()

    for csv_files_term, title_prefix in csv_files_term:
        df = read_csv(csv_files_term)
        df_selected = df[columns_item]
        total_volume[title_prefix] = df_selected.sum()      

    return plot_bar_graph('', columns_item, total_volume)


def plot_bar_graph(title, columns_item, total_volume):
    fig, ax = plt.subplots(figsize=(12, 6))

    total_volume.plot(kind='bar', ax=ax, width=0.8)    # 그룹화된 막대 그래프 생성

    ax.set_ylabel('운송량')
    ax.set_title(f'{title} 기간별 운송량')
    ax.set_xticklabels(columns_item, rotation=45, ha="right")
    ax.legend(title='기간', bbox_to_anchor=(1, 1), loc='upper left', fontsize=10)
    
    # plt.text() - 진행중! 막대 그래프 위에 값 표시 (for문)

    bar_img_io = io.BytesIO()    # 그래프 이미지 저장
    plt.savefig(bar_img_io, format='png', bbox_inches='tight')
    bar_img_io.seek(0)
    bar_item_img = base64.b64encode(bar_img_io.getvalue()).decode()
    plt.close()

    return bar_item_img


def bar_analysis(csv_files_term, columns_item):
    total_volume = pd.DataFrame()
    
    for file_path, title_prefix in csv_files_term:
        df = read_csv(file_path)
        df_selected = df[columns_item]
        total_volume[title_prefix] = df_selected.sum()
    
    # 각 기간별 총 운송량과 평균 구하기
    high_bar_period = total_volume.sum(axis=0).idxmax()
    high_bar_volume = total_volume[high_bar_period].mean()
    low_bar_period = total_volume.sum(axis=0).idxmin()
    low_bar_volume = total_volume[low_bar_period].mean()
    
    return high_bar_period, high_bar_volume, low_bar_period, low_bar_volume


def plot_line_graph(df, columns_item, title):
    df_monthly = df[columns_item].resample('ME').sum()
    fig, ax = plt.subplots(figsize=(17, 4))

    for column in columns_item:
        ax.plot(df_monthly.index, df_monthly[column], label=column)
        
    ax.set_title(title)
    ax.set_ylabel('운송량')
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%y.%m'))
    ax.legend(loc='upper left', bbox_to_anchor=(1, 1))
    plt.tight_layout()

    line_img_io = io.BytesIO()
    plt.savefig(line_img_io, format='png')
    line_img_io.seek(0)
    line_item_img = base64.b64encode(line_img_io.getvalue()).decode()
    plt.close()

    return line_item_img


def line_analysis(csv_files_term, columns_item):
    monthly_avg_volume = {}  # 월별 평균 운송량
    total_avg_volume = []    # 전체 운송량 리스트

    for file_path, title_prefix in csv_files_term:
        df = read_csv(file_path)
        df['배송년월일'] = pd.to_datetime(df['배송년월일'], format='%Y%m%d')
        df.set_index('배송년월일', inplace=True)

        # 월별 데이터 집계
        df_monthly = df[columns_item].resample('M').sum()
        total_avg_volume.extend(df_monthly.sum(axis=1).values)
        
# 전체 운송량 데이터를 날짜별로 설정
    total_avg_volume = pd.Series(total_avg_volume, index=pd.date_range(start=df_monthly.index[0], periods=len(total_avg_volume), freq='M'))
    monthly_avg_volume = total_avg_volume.mean() # 월별 평균 운송량

    # 가장 운송량이 많았던 월과 적었던 월
    max_month = total_avg_volume.idxmax()
    min_month = total_avg_volume.idxmin()

    # 결과 형식 지정
    high_month = (max_month.year, max_month.month, f"{total_avg_volume[max_month]:,}")
    low_month = (min_month.year, min_month.month, f"{total_avg_volume[min_month]:,}")
    monthly_avg_volume = f"{monthly_avg_volume:,.0f}"

    return high_month, low_month, monthly_avg_volume


def plot_weekday_line_graph(file_path, columns_item):
    df = read_csv(file_path)
    df['배송년월일'] = pd.to_datetime(df['배송년월일'], format='%Y%m%d')
    df.set_index('배송년월일', inplace=True)
    
    df['요일'] = df.index.dayofweek  # 요일 계산
    df_weekday = df[df['요일'] < 5]  # 주말 필터링
    
    weekday_sum = df_weekday.groupby('요일')[columns_item].sum()
    
    fig, ax = plt.subplots(figsize=(7, 4))
    weekday_sum.plot(ax=ax)

    ax.set_title('요일별 운송량')
    ax.set_ylabel('운송량')
    ax.set_xticks(range(5))
    ax.set_xticklabels(['월', '화', '수', '목', '금'])
    ax.legend(loc='upper left', bbox_to_anchor=(1, 1))
    plt.tight_layout()
    
    #     # mplcursors를 사용하여 마우스 오버 시 팝업
    # cursor = mplcursors.cursor(ax, hover=True)  # hover=True로 마우스 오버 시에도 팝업이 뜬다.
    
    # cursor.connect("add", lambda sel: sel.annotation.set_text(
    #     f'<p style="font-size: 14px; font-weight: bold; color: #0047AB;">요일: {["월", "화", "수", "목", "금", "토", "일"][sel.target[0]]}</p>'
    #     f'<p style="font-size: 12px; color: #555;">운송량: {sel.target[1]:,.0f} 건</p>'
    # ))

    weekday_line_img_io = io.BytesIO()
    plt.savefig(weekday_line_img_io, format='png')
    weekday_line_img_io.seek(0)
    weekday_volume = base64.b64encode(weekday_line_img_io.getvalue()).decode()
    plt.close()

    return weekday_volume


def weekday_line_analysis(csv_files_all, columns_item):
    df = pd.concat([read_csv(file_path) for file_path, _ in csv_files_all], ignore_index=True)
    df['배송년월일'] = pd.to_datetime(df['배송년월일'], format='%Y%m%d')
    df.set_index('배송년월일', inplace=True)
    
    # 요일별로 운송량 합계 계산 (주말 제외)
    df['요일'] = df.index.dayofweek
    df_weekday = df[df['요일'] < 5]  # 주말 필터링 (0:월~4:금)
    weekday_sum = df_weekday.groupby('요일')[columns_item].sum()
    weekday_avg = weekday_sum.mean(axis=1)

    high_day, low_day = weekday_avg.idxmax(), weekday_avg.idxmin()
    
    days_of_week = ['월', '화', '수', '목', '금']
    return {
        'high_day': days_of_week[high_day],
        'high_day_mean': round(weekday_avg.max(), 2),
        'low_day': days_of_week[low_day],
        'low_day_mean': round(weekday_avg.min(), 2),
    }


# 여기부터 듀얼맵

def color_map(csv_files_term, columns_item):  # 운송량 집계, 색상 매핑
    df = pd.concat([read_csv(file_path) for file_path, _ in csv_files_term], ignore_index=True)
    df.columns = df.columns.str.strip()
    
    df['운송량'] = df[columns_item].sum(axis=1)
    
    def gu_rank(group_by_col):
        rank = df.groupby(group_by_col)['운송량'].sum().reset_index()
        rank = rank.sort_values(by='운송량', ascending=False).reset_index(drop=True)
        
        # 운송량 비율에 따라 색상 조정
        cmap = plt.cm.Blues
        norm = plt.Normalize(vmin=rank['운송량'].min(), vmax=rank['운송량'].max())  # 운송량 범위 정규화
        rank['색상'] = rank['운송량'].apply(
            lambda x: mcolors.to_rgba(cmap(norm(x)))  # 운송량 별 색상 계산
        )

        rank.columns = [group_by_col, '운송량', '색상']
        return rank

    sender_rank = gu_rank('송하인_구명') 
    receiver_rank = gu_rank('수하인_구명') 
    dual_map = generate_dual_map(sender_rank, receiver_rank)

    return dual_map


def generate_dual_map(sender_rank, receiver_rank):
    with open('apps/logistics/서울_자치구_경계_2017.geojson', 'r', encoding='utf-8') as f:
        geojson = json.load(f)
    
    m = folium.plugins.DualMap(location=[37.5665, 126.9780], zoom_start=11, max_zoom = 15, min_zoom=7)  # 서울 중심 좌표
    
    def color_opacity(volume, max_volume):
        return 0.2 + (volume / max_volume) * 0.8


    def color_gu(volume, max_volume):
        opacity = color_opacity(volume, max_volume)
        return mcolors.to_rgba('#0047AB', alpha=opacity)
        
    
    def sender_geojson():            
        max_sender_volume = sender_rank['운송량'].max()
        
        for feature in geojson['features']:
            districts_name = feature['properties']['SIG_KOR_NM']  # 구 이름
            data = sender_rank[sender_rank['송하인_구명'] == districts_name]
            
            gu_name = data['송하인_구명'].iloc[0]
            total_volume = data['운송량'].iloc[0]
            rank_sender = data.index[0] + 1
            
            color = color_gu(total_volume, max_sender_volume)   
            
            folium.GeoJson(
                feature,
                style_function=lambda feature, color=color: {
                    'fillColor': "#0047AB", # cj blue
                    'color': color,
                    'weight': 1,
                    'fillOpacity': color[3]
                },
                popup = folium.Popup(f"""
                    <p style="font-size: 13px; font-weight: bold; color: #0047AB; line-height: 1.2; margin-bottom: 0;">{gu_name} ({rank_sender}위)</p>
                    <p style="font-size: 11px; line-height: 1.2; margin-top: 0; margin-bottom: 0;">{total_volume} 건</p>
                """, max_width=300)).add_to(m.m1)
    
    
    def receiver_geojson():
        max_receiver_volume = receiver_rank['운송량'].max()
        
        for feature in geojson['features']:
            districts_name = feature['properties']['SIG_KOR_NM']
            data = receiver_rank[receiver_rank['수하인_구명'] == districts_name]

            gu_name = data['수하인_구명'].iloc[0]
            total_volume = data['운송량'].iloc[0]
            rank_receiver = data.index[0] + 1
            
            
            color = color_gu(total_volume, max_receiver_volume)
            
            folium.GeoJson(
                feature,
                style_function=lambda feature, color=color: {
                    'fillColor': "#2E7D32",
                    'color': color,
                    'weight': 1,
                    'fillOpacity': color[3]
                },
                popup = folium.Popup(f"""
                    <p style="font-size: 13px; font-weight: bold; color: #0047AB; line-height: 1.2; margin-bottom: 0;">{gu_name} ({rank_receiver}위)</p>
                    <p style="font-size: 11px; line-height: 1.2; margin-top: 0; margin-bottom: 0;">{total_volume} 건</p>
                """, max_width=300)).add_to(m.m2)

    sender_geojson()
    receiver_geojson()

    sender_text, receiver_text, combined_text = map_analysis(sender_rank, receiver_rank)

    dual_map_file_path = os.path.join('apps/logistics/static/images', 'dual_map.html')
    m.save(dual_map_file_path)

    return dual_map_file_path, sender_text, receiver_text, combined_text


# 지도 요약 - 지역 별 수요 top 3
def map_analysis(sender_rank, receiver_rank):
    
    all_volume = sender_rank.copy()
    all_volume['송수하인_합계'] = all_volume['운송량'] + receiver_rank['운송량']
    
    top_sender = sender_rank.nlargest(1, '운송량')['송하인_구명'].iloc[0]
    top_receiver = receiver_rank.nlargest(1, '운송량')['수하인_구명'].iloc[0]
    
    # 송수하인 합계 순위
    top_combined = all_volume.nlargest(3, '송수하인_합계')[['송하인_구명', '송수하인_합계']]
    combined_text = " - ".join([f"{row['송하인_구명']} ({row['송수하인_합계']} 건)" for _, row in top_combined.iterrows()])

    return top_sender, top_receiver, combined_text