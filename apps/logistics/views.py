import folium.plugins
import matplotlib, io, os, base64, json, folium, chardet
matplotlib.use('Agg')
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib import font_manager
import pandas as pd
import geopandas as gpd
from flask import Blueprint, render_template

# 한글 폰트 설정 (윈도우 맑은 고딕)
font_path = "C:/Windows/Fonts/malgun.ttf"
font_prop = font_manager.FontProperties(fname=font_path)
plt.rcParams['font.family'] = font_prop.get_name()
plt.rcParams['axes.unicode_minus'] = False  # 마이너스 기호 깨짐 방지

logistics = Blueprint('logistics', __name__, template_folder='templates', static_folder='static')
geojson_path = os.path.join('apps', 'logistics', '서울_자치구_경계_2017.geojson')

colors = [
    "#FF5733", "#33FF57", "#5733FF", "#FFD700", "#FF33A8", "#33FFF6", "#FF8C33",
    "#B833FF", "#33FF99", "#FFC733", "#5733A8", "#A833FF", "#33A8FF", "#FF5733",
    "#A8FF33", "#33FFB8", "#FF33D7", "#FF6F33", "#5733A8", "#B8FF33", "#33FFAA",
    "#FF33F6", "#FF3333", "#33FF8C", "#33D7FF"
]


@logistics.route('/')
def logistics_page():
    csv_files_all = [
        ('apps/logistics/logi_all.csv', '전체 기간 (2018~2024)')
    ]
    csv_files_term = [
        ('apps/logistics/logi_before.csv', '코로나 이전 (2018.01 ~ 2019.12)'),
        ('apps/logistics/logi_during.csv', '코로나 기간 (2020.01 ~ 2022.04)'),
        ('apps/logistics/logi_after.csv', '코로나 이후 (2022.05 ~ 2023.12)')
    ]
    
    pie_item_img, line_item_img, weekday_line_img, columns_item  = logistics_graph(csv_files_all, csv_files_term)
    bar_item_img = logistics_bar_graph(csv_files_term)
    
    dual_map = logistics_volume_map(csv_files_term, columns_item )    # 송하인, 수하인 지도 생성
    
    return render_template('logistics.html', 
                           pie_plot_urls=pie_item_img, 
                           line_plot_urls=line_item_img, 
                           weekday_line_plot_urls=weekday_line_img,
                           bar_plot_urls=bar_item_img,
                           dual_map=dual_map)


def read_csv(file_path):
    with open(file_path, 'rb') as f:
        encoding = chardet.detect(f.read(1000))['encoding'] # 파일의 첫 1000바이트만 읽어 인코딩 추정
   
    return pd.read_csv(file_path, encoding=encoding) 


def logistics_graph(csv_files_all, csv_files_term):
    pie_item_img, line_item_img, weekday_line_img = [], [], []
    columns_item = [
        '가구/인테리어', '도서/음반', '디지털/가전', '생활/건강', 
        '스포츠/레저', '식품', '출산/육아', '패션의류', '패션잡화', '화장품/미용'
    ]

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
    df = read_csv(file_path)
    df['배송년월일'] = pd.to_datetime(df['배송년월일'], format='%Y%m%d')
    df.set_index('배송년월일', inplace=True)
    
    total_volume = df[columns_item].sum()
    
    bar_item = plot_bar_graph(title_prefix, columns_item, total_volume)
    pie_item = plot_pie_graph(total_volume, title_prefix)
    line_item = plot_line_graph(df, columns_item, title_prefix)

    return bar_item, pie_item, line_item
    
    
def logistics_bar_graph(csv_files_term):
    columns_item = [
        '가구/인테리어', '도서/음반', '디지털/가전', '생활/건강', 
        '스포츠/레저', '식품', '출산/육아', '패션의류', '패션잡화', '화장품/미용'
    ]
    total_volume = pd.DataFrame()    # 모든 기간의 데이터 총합을 구해서 하나의 막대 그래프 이미지 생성

    for file_path, title_prefix in csv_files_term:
        df = read_csv(file_path)
        df_selected = df[columns_item]
        total_volume[title_prefix] = df_selected.sum()      

    return plot_bar_graph('코로나 기간별 운송량', columns_item, total_volume)  # 총합을 기준으로 막대 그래프 생성


def plot_bar_graph(title, columns_item, total_volume):
    fig, ax = plt.subplots(figsize=(12, 6))

    total_volume.plot(kind='bar', ax=ax, width=0.8)    # 그룹화된 막대 그래프 생성

    ax.set_ylabel('운송량')
    ax.set_title(f'{title} 기간별 운송량')
    ax.set_xticklabels(columns_item, rotation=45, ha="right")
    ax.legend(title='기간', bbox_to_anchor=(1, 1), loc='upper left', fontsize=10)

    bar_img_io = io.BytesIO()    # 그래프 이미지 저장
    plt.savefig(bar_img_io, format='png', bbox_inches='tight')
    bar_img_io.seek(0)
    bar_item_img = base64.b64encode(bar_img_io.getvalue()).decode()
    plt.close()

    return bar_item_img

def plot_pie_graph(data, title):
    sorted_data = data.sort_values(ascending=False)
    colors = plt.cm.Paired(range(len(sorted_data)))
    
    plt.figure(figsize=(6, 6))
    wedges = plt.pie(sorted_data, autopct='%1.1f%%', startangle=90, colors=colors)
    plt.legend(wedges, sorted_data.index, loc='upper left', bbox_to_anchor=(1, 1), fontsize=10)

    plt.tight_layout()
    plt.title(f'{title}')

    pie_img_io = io.BytesIO()
    plt.savefig(pie_img_io, format='png')
    pie_img_io.seek(0)
    pie_item_img = base64.b64encode(pie_img_io.getvalue()).decode()
    plt.close()

    return pie_item_img


def plot_line_graph(df, columns_item, title):
    df_monthly = df[columns_item].resample('ME').sum()
    fig, ax = plt.subplots(figsize=(17, 4))

    for column in columns_item:
        ax.plot(df_monthly.index, df_monthly[column], label=column)
        
    ax.set_title(title)
    ax.set_xlabel('기간(년.월)')
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


def plot_weekday_line_graph(csv_files_all, columns_item):
    df = read_csv(csv_files_all)
    df['배송년월일'] = pd.to_datetime(df['배송년월일'], format='%Y%m%d')
    df.set_index('배송년월일', inplace=True)
    df['요일'] = df.index.dayofweek
    weekday_sum = df.groupby('요일')[columns_item].sum()
    
    fig, ax = plt.subplots(figsize=(7, 4))
    weekday_sum.plot(ax=ax)

    ax.set_title('요일별 운송량')
    ax.set_xlabel('요일')
    ax.set_ylabel('운송량')
    ax.set_xticks(range(7))
    ax.set_xticklabels(['월', '화', '수', '목', '금', '토', '일'])
    ax.legend(loc='upper left', bbox_to_anchor=(1, 1))
    plt.tight_layout()

    weekday_line_img_io = io.BytesIO()
    plt.savefig(weekday_line_img_io, format='png')
    weekday_line_img_io.seek(0)
    weekday_volume = base64.b64encode(weekday_line_img_io.getvalue()).decode()
    plt.close()

    return weekday_volume

# 여기서부터 듀얼맵

def logistics_volume_map(csv_files_term, columns_item):  # 송하인과 수하인 구별로 운송량 집계, 지도에 표시
    df = pd.concat([read_csv(file) for file, _ in csv_files_term], ignore_index=True)
    df.columns = df.columns.str.strip()
    
    df['운송량'] = df[columns_item].sum(axis=1)
    # print(df) 
    
    # 각 행의 품목별 운송량 합산 # 9번 열부터 끝까지 품목별 운송량 합산
    # df['운송량'] = df.iloc[:, 9:].sum(axis=1)

    sender_rank = gu_color(df, '송하인_구명')
    receiver_rank = gu_color(df, '수하인_구명')
    # print(sender_rank)
    # print('='*50)    

        # 송하인과 수하인 구별 운송량 순위를 반환
    # sender_map = generate_dual_map(sender_rank, receiver_rank, 'sender')
    # receiver_map = generate_dual_map(sender_rank, receiver_rank, 'receiver')
    
    # 송하인과 수하인에 대한 듀얼 맵 생성
    dual_map = generate_dual_map(sender_rank, receiver_rank)

    return dual_map

def gu_color(df, column_rank):   # 각 구별 운송량 집계 및 색상 계산
    df['운송량'] = df.iloc[:, 9:].sum(axis=1)  
    
    # df['운송량'] = df[columns_item].sum(axis=1)  # 품목별 운송량 합산
    # print(df)
    rank = df.groupby(column_rank)['운송량'].sum().reset_index()
    rank = rank.sort_values(by='운송량', ascending=False).reset_index(drop=True)
    # 색상 계산: '운송량'의 비율에 따라 색상 조정
    rank['색상'] = rank['운송량'].apply(
        lambda x: mcolors.to_rgba("#0047AB", alpha=0.1 + (x / rank['운송량'].max()) * 0.9)
    )
    rank.columns = [column_rank, '운송량', '색상']
    
    return rank


def generate_dual_map(sender_rank, receiver_rank):
    with open('apps/logistics/서울_자치구_경계_2017.geojson', 'r', encoding='utf-8') as f:
        geojson = json.load(f)

    # # 송하인 맵의 운송량 색상을 매핑하는 함수
    # def sender_geojson():
    #     for idx, feature in enumerate(geojson['features']):
    #             gu_name = feature['properties']['SIG_KOR_NM']
    #             total_volume = sender_rank['운송량']
    #             color = sender_rank['색상'][idx] # 그냥 색상임

    #             folium.GeoJson(
    #                 feature,
    #                 style_function= lambda feature, color=color: {
    #                 'fillColor': color,
    #                 'color': '#0047AB',
    #                 'weight': 2,
    #                 'fillOpacity': 0.6
    #                 },
    #         popup=folium.Popup(f'<p>{gu_name}</p>')
    #     ).add_to(m.m1)
    
    # def receiver_geojson():
        
    
    m = folium.plugins.DualMap(location=[37.5665, 126.9780], zoom_start=11)  # 서울의 중심 좌표로 듀얼맵 생성
    # geo = gdf[gdf['SGG_NM'] == f'서울특별시 {gu_name}']
        # if not geo.empty:
            # GeoJson 객체 생성 및 색상 설정
            # geojson = geo.geometry.__geo_interface__
    def sender_geojson():
        # for _, column in sender_rank.iterrows():
        #     gu_name = column[0]
        #     total_volume = column[1]
        #     color = column[2]
            # color = mcolors.to_rgba("#0047AB", alpha=0.1 + (total_volume / sender_rank[3].max()) * 0.9) -> sender_rank에서 이미 계산됨

            # geo = gdf[gdf['SGG_NM'] == f'서울특별시 {gu_name}']
            # if not geo.empty:
                # GeoJson 객체 생성 및 색상 설정
                # geojson = geo.geometry.__geo_interface__
                
        for idx, feature in enumerate(geojson['features']):
            districts_name = feature['properties']['SIG_KOR_NM'] # 구 이름
            data = sender_rank[sender_rank['송하인_구명'] == districts_name]
            gu_name = data['송하인_구명'].iloc[0]
            total_volume = data['운송량'].iloc[0]
            color = data['색상'].iloc[0]
            # color = mcolors.to_rgba("#0047AB", alpha=0.1 + (total_volume / sender_rank['운송량'].max()) * 0.9)
            color = colors[idx] # 나중에 색상 처리하고 변경하셈
            
            print("="*50)
            print(data)
            
            folium.GeoJson(
                feature,
                style_function=lambda feature, color=color: {
                    'fillColor': color,
                    'color': color,
                    'weight': 1,
                    'fillOpacity': 0.6
                },
                popup=folium.Popup(f"<p>{gu_name} - {total_volume} 건</p>")
            ).add_to(m.m1)
    
    # # 수하인 맵의 운송량 색상을 매핑하는 함수
    def receiver_geojson():
        for _, column in receiver_rank.iterrows():
            gu_name = column[0]
            total_volume = column[1]
            color = column[2]

            # geo = gdf[gdf['SGG_NM'] == f'서울특별시 {gu_name}']
            
            # print('=====================================')
            # print(gu_name)
            # print(total_volume)
            # print(color)
            # print(gdf[gdf['SGG_NM'] == f'서울특별시 {gu_name}'])
            # print('=====================================')

            
            # if not geo.empty:
                # GeoJson 객체 생성 및 색상 설정
                # geojson = geo.geometry.__geo_interface__
            folium.GeoJson(
                geojson,
                style_function=lambda feature, color=color: {
                    'fillColor': color,
                    'color': color,
                    'weight': 1,
                    'fillOpacity': 0.6
                },
                popup=f"{gu_name} - {total_volume} 건"
            ).add_to(m.m2)
    
    #송하인 및 수하인 GeoJson 추가
    sender_geojson()
    receiver_geojson()

    # # HTML로 저장
    dual_map_file_path = os.path.join('apps/logistics/static/maps', 'dual_map.html')
    m.save(dual_map_file_path)

    return dual_map_file_path
