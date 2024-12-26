from flask import Blueprint, render_template
import folium.plugins
import pandas as pd
import matplotlib, io, os, base64, json, folium, chardet
matplotlib.use('Agg')
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib import font_manager
import mplcursors


font_path = "C:/Windows/Fonts/malgun.ttf"
font_prop = font_manager.FontProperties(fname=font_path)
plt.rcParams['font.family'] = font_prop.get_name()
plt.rcParams['axes.unicode_minus'] = False  # 마이너스 기호 깨짐 방지

logistics = Blueprint('logistics', __name__, template_folder='templates', static_folder='static')
geojson_path = os.path.join('apps', 'logistics', '서울_자치구_경계_2017.geojson')


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
    
    pie_item_img, line_item_img, weekday_line_img, columns_item = logistics_graph(csv_files_all, csv_files_term)
    bar_item_img = logistics_bar_graph(csv_files_term)
    
    dual_map = color_map(csv_files_term, columns_item )
    
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

    return plot_bar_graph('코로나 기간별 운송량', columns_item, total_volume)


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


# 여기서부터 듀얼맵

def color_map(csv_files_term, columns_item):  # 운송량 집계, 색상 매핑
    df = pd.concat([read_csv(file) for file, _ in csv_files_term], ignore_index=True)
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
    
    # print('='*50)    
    # print(sender_rank)
    # print('='*50)    
    # print(receiver_rank)

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

    dual_map_file_path = os.path.join('apps/logistics/static/maps', 'dual_map.html')
    m.save(dual_map_file_path)

    return dual_map_file_path
