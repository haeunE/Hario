import matplotlib
matplotlib.use('Agg')
import os
import io
import base64
import folium
from folium.plugins import HeatMap
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib import font_manager
import pandas as pd
from flask import Blueprint, render_template
import chardet

# 한글 폰트 설정 (윈도우 맑은 고딕)
font_path = "C:/Windows/Fonts/malgun.ttf"
font_prop = font_manager.FontProperties(fname=font_path)
plt.rcParams['font.family'] = font_prop.get_name()
plt.rcParams['axes.unicode_minus'] = False  # 마이너스 기호 깨짐 방지

logistics = Blueprint('logistics', __name__, template_folder='templates', static_folder='static')

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
    
    pie_item_img, line_item_img, weekday_line_img = logistics_graph(csv_files_all, csv_files_term)
    bar_item_img = logistics_bar_graph(csv_files_term)
    # sender_map, receiver_map = logistics_volume_map(csv_files_term)
    
    return render_template('logistics.html', 
                           pie_plot_urls=pie_item_img, 
                           line_plot_urls=line_item_img, 
                           weekday_line_plot_urls=weekday_line_img,
                           bar_plot_urls=bar_item_img)


def read_csv(file_path):
    with open(file_path, 'rb') as f:
        # 파일의 첫 1000바이트만 읽어 인코딩 추정
        encoding = chardet.detect(f.read(1000))['encoding']
   
    return pd.read_csv(file_path, encoding=encoding) 

    # try:
    #     return pd.read_csv(file_path, encoding=encoding)
    # except UnicodeDecodeError:
    #     return pd.read_csv(file_path, encoding='utf-8')


def logistics_graph(csv_files_all, csv_files_term):
    pie_item_img, line_item_img, weekday_line_img = [], [], []
    columns_item = [
        '가구/인테리어', '도서/음반', '디지털/가전', '생활/건강', 
        '스포츠/레저', '식품', '출산/육아', '패션의류', '패션잡화', '화장품/미용'
    ]

    # 전체 기간에 대해 파이형 그래프와 선형 그래프 생성 (csv_files_all)
    for file_path, title_prefix in csv_files_all:
        bar_item, pie_item, line_item = generate_graph(file_path, title_prefix, columns_item)
        pie_item_img.append(pie_item)
        line_item_img.append(line_item)

    # 코로나 이전, 코로나 기간, 코로나 이후에 대한 파이형 그래프와 선형 그래프 생성 (csv_files_term)
    for file_path, title_prefix in csv_files_term:
        bar_item, pie_item, line_item = generate_graph(file_path, title_prefix, columns_item)
        pie_item_img.append(pie_item)
        line_item_img.append(line_item)

    # 전체 기간 요일별 선형 그래프
    weekday_line_img.append(plot_weekday_line_graph('apps/logistics/logi_all.csv', columns_item))
    
    return pie_item_img, line_item_img, weekday_line_img


def generate_graph(file_path, title_prefix, columns_item):
    df = read_csv(file_path)
    df['배송년월일'] = pd.to_datetime(df['배송년월일'], format='%Y%m%d')
    df.set_index('배송년월일', inplace=True)
    
    total_volume = df[columns_item].sum()
    
    bar_item = plot_bar_graph(title_prefix, columns_item, total_volume)
    pie_item = plot_pie_graph(total_volume, title_prefix)
    line_item = plot_line_graph(df, columns_item, title_prefix)

    return bar_item, pie_item, line_item
    # df_selected = df[columns_item]

    # bar_item = plot_bar_graph(title_prefix, columns_item, total_volume)
    # pie_item = plot_pie_graph(df_selected.sum(), title_prefix)
    # line_item = plot_line_graph(df, columns_item, title_prefix)

    # return bar_item, pie_item, line_item

def logistics_bar_graph(csv_files_term):
    # bar_item_img = []
    columns_item = [
        '가구/인테리어', '도서/음반', '디지털/가전', '생활/건강', 
        '스포츠/레저', '식품', '출산/육아', '패션의류', '패션잡화', '화장품/미용'
    ]
   
    # 모든 기간의 데이터를 합친 뒤 총합을 구해서 하나의 막대 그래프 이미지 생성
    total_volume = pd.DataFrame()

    for file_path, title_prefix in csv_files_term:
        df = read_csv(file_path)
        df_selected = df[columns_item]
        total_volume[title_prefix] = df_selected.sum()
        
    print(total_volume)
    
    # 총합을 기준으로 막대 그래프 생성
    return plot_bar_graph('코로나 기간별 운송량', columns_item, total_volume)
   
    
    # for file_path, title_prefix in csv_files_term:
    #     df = read_csv(file_path)
    #     df_selected = df[columns_item]
    #     total_volume = df_selected.sum().sort_values(ascending=False)
    #     bar_item_img.append(plot_bar_graph(title_prefix, columns_item, total_volume))
        
    # return bar_item_img 


def plot_bar_graph(title, columns_item, total_volume):
    fig, ax = plt.subplots(figsize=(12, 6))
       # 그룹화된 막대 그래프 생성 (각 품목에 대해 3개의 기간별 값)
    total_volume.plot(kind='bar', ax=ax, width=0.8)

    # 그래프 레이블 및 제목 설정
    ax.set_ylabel('운송량')
    ax.set_title(f'{title} 기간별 운송량')
    ax.set_xticklabels(columns_item, rotation=45, ha="right")

    # 범례(legend) 설정: 기간별 색상 구분
    ax.legend(title='기간', bbox_to_anchor=(1, 1), loc='upper left', fontsize=10)

    # 그래프 이미지 저장
    bar_img_io = io.BytesIO()
    plt.savefig(bar_img_io, format='png', bbox_inches='tight')
    bar_img_io.seek(0)
    bar_item_img = base64.b64encode(bar_img_io.getvalue()).decode()
    plt.close()

    return bar_item_img

def plot_pie_graph(data, title):
    sorted_data = data.sort_values(ascending=False)
    colors = plt.cm.Paired(range(len(sorted_data)))
    
    plt.figure(figsize=(6, 6))
    wedges, texts, autotexts = plt.pie(sorted_data, autopct='%1.1f%%', startangle=90, colors=colors)
    plt.legend(wedges, sorted_data.index, loc='upper left', bbox_to_anchor=(1, 1), fontsize=10)

    plt.tight_layout()
    plt.title(f'{title}')

    pie_img_io = io.BytesIO()
    plt.savefig(pie_img_io, format='png')
    pie_img_io.seek(0)
    pie_item_img = base64.b64encode(pie_img_io.getvalue()).decode()
    plt.close()

    return pie_item_img


# 전체 / 기간별 파이그래프
# def plot_pie_graph(data, title, show_legend=True):
#     sorted_data = data.sort_values(ascending=False) # 범례 비율 높은-낮은 순 정렬
#     colors = plt.cm.Paired(range(len(sorted_data)))
    
#     plt.figure(figsize=(6, 6))
#     wedges, texts, autotexts = plt.pie(
#         sorted_data, 
#         labels=None,
#         autopct='%1.1f%%', 
#         startangle=90, 
#         colors=colors
#     )
    
#     if show_legend:
#         plt.legend(wedges, sorted_data.index, loc='upper left', bbox_to_anchor=(1, 1), 
#                    fontsize=10, handlelength=1, handleheight=1)
    
#     plt.tight_layout()
#     plt.title(f'{title}')

#     pie_img_io = io.BytesIO()
#     plt.savefig(pie_img_io, format='png')
#     pie_img_io.seek(0)
#     pie_item_img = base64.b64encode(pie_img_io.getvalue()).decode()
#     plt.close()

#     return pie_item_img


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


def generate_map(rank):
    district_coords = {
        '종로구': [37.5702, 126.9794],
        '중구': [37.5636, 126.9977],
        '용산구': [37.5326, 126.9905],
        '성동구': [37.5634, 127.0404],
        '광진구': [37.5383, 127.0722],
        '동대문구': [37.5742, 127.0391],
        '중랑구': [37.6063, 127.0922],
        '성북구': [37.6114, 127.0175],
        '강북구': [37.6387, 127.0255],
        '도봉구': [37.6684, 127.0286],
        '노원구': [37.6554, 127.0774],
        '은평구': [37.6040, 126.9297],
        '서대문구': [37.5796, 126.9354],
        '마포구': [37.5663, 126.9000],
        '양천구': [37.5173, 126.8668],
        '강서구': [37.5501, 126.8493],
        '구로구': [37.4950, 126.8837],
        '금천구': [37.4550, 126.9009],
        '영등포구': [37.5260, 126.8973],
        '동작구': [37.5041, 126.9386],
        '관악구': [37.4783, 126.9523],
        '서초구': [37.4837, 127.0320],
        '강남구': [37.4979, 127.0276],
        '송파구': [37.5146, 127.1065],
        '강동구': [37.5300, 127.1232]
    }
    
    # static/images 폴더 경로 설정
    # images_folder = os.path.join(os.path.dirname(__file__), 'static', 'images')

    m = folium.Map(location=[37.5665, 126.9780], zoom_start=11)

    for _, row in rank.iterrows():
        # print(row[0], row[1], row[2])  # '송하인_구명', '운송량', '색상' 출력
        district = row[0]
        color = map_color(row['운송량'], rank['운송량'].max())
        
        if district in district_coords:
            lat, lon = district_coords[district]
            folium.CircleMarker(
                location=[lat, lon],
                radius=10,
                color=color,
                fill=True,
                fill_color=color,
                fill_opacity=0.6,
                popup=f"{district}: {row['운송량']}"
            ).add_to(m)
        else:
            print(f"Warning: {district} not found in district_coords")
        

    # 지도 파일을 static/images 폴더에 저장
    map_filename = "term.html"
    images_folder = os.path.join(os.path.dirname(__file__), 'static', 'images')
    map_path = os.path.join(images_folder, map_filename)
    m.save(map_path)
    
    return f"images/{map_filename}"


def volume_rank(df, column_rank):
    # 데이터 집계 및 색상 계산
    rank = df[column_rank].value_counts().reset_index()

    rank.columns = [column_rank, '운송량']
    rank['색상'] = rank['운송량'].apply(
        lambda x: mcolors.to_rgba("#0047AB", alpha=0.1 + (x / rank['운송량'].max()) * 0.9)
    )
    return rank


def map_color(volume, max_volume):
    # 운송량에 따라 색상 동적으로 설정
    cj_blue = "#0047AB"
    alpha = 0.1 + (volume / max_volume) * 0.9  # 밝기
    return mcolors.to_rgba(cj_blue, alpha=alpha)


# 송하인과 수하인 구별로 운송량 집계, 지도에 표시
def logistics_volume_map(csv_files_term):
    df_all = pd.concat([read_csv(file) for file, _ in csv_files_term])

    # 송하인과 수하인 운송량 순위
    sender_rank = volume_rank(df_all, '송하인_구명')
    receiver_rank = volume_rank(df_all, '수하인_구명')

    # 지도 생성
    sender_map = generate_map(sender_rank)
    receiver_map = generate_map(receiver_rank)
    
    return sender_map, receiver_map



