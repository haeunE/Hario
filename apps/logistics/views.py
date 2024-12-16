from flask import Flask
import io
import base64
import matplotlib.pyplot as plt
import pandas as pd
from flask import Blueprint, render_template
from matplotlib.ticker import FormatStrFormatter
import pandas as pd

logistics = Blueprint('logistics', __name__, template_folder='templates', static_folder='static')

@logistics.route('/')
def logistics_page():
    pie_img_base64, line_img_base64 = logistics_graph()  # 함수 호출로 데이터 처리
    return render_template('logistics.html', pie_plot_urls=pie_img_base64, line_plot_urls=line_img_base64)

def logistics_graph():
    csv_files = [
    'apps/logistics/logi_all.csv',
    'apps/logistics/logi_before.csv',
    'apps/logistics/logi_during.csv',
    'apps/logistics/logi_after.csv'
    ]
    
    pie_img_base64 = []
    line_img_base64 = []
    
    for csv_file in csv_files:
        pie_base64, line_base64 = generate_graph(csv_file)
        pie_img_base64.append(pie_base64)
        line_img_base64.append(line_base64)

    return pie_img_base64, line_img_base64

# 그래프 생성
def generate_graph(csv_file):
    df = pd.read_csv(csv_file, encoding='utf-8')
    
    df['배송년월일'] = pd.to_datetime(df['배송년월일'], format='%Y%m%d').dt.to_period('W')
    df.set_index('배송년월일', inplace=True)

    df_sum = df.reset_index().groupby('배송년월일').sum().reset_index()
    df_sum['배송년월일'] = df_sum['배송년월일'].dt.to_timestamp()

    columns_to_plot = [
        '가구/인테리어',
        '기타',
        '도서/음반',
        '디지털/가전',
        '생활/건강',
        '스포츠/레저',
        '식품',
        '출산/육아',
        '패션의류',	
        '패션잡화',	
        '화장품/미용'
    ]
    df_selected = df[columns_to_plot]
    total_logistics_per_item = df_selected.sum()

    # 파이형 그래프 생성
    plt.figure(figsize=(10, 10))
    plt.pie(total_logistics_per_item, labels=total_logistics_per_item.index, autopct='%1.1f%%', startangle=90)
    plt.title('품목 별 운송 비율')

    pie_img_io = io.BytesIO()
    plt.savefig(pie_img_io, format='png')
    pie_img_io.seek(0)
    pie_img_base64 = base64.b64encode(pie_img_io.getvalue()).decode()
    plt.close()

    plt.figure(figsize=(10, 7))
    for column in df_sum.columns[1:]:
        plt.plot(df_sum['배송년월일'], df_sum[column], label=column)

    plt.title('품목 별 운송량')
    plt.xlabel('기간')
    plt.ylabel('운송량')

    plt.gca().yaxis.set_major_formatter(FormatStrFormatter('%d'))
    plt.legend(loc='upper left', bbox_to_anchor=(1, 1))
    plt.tight_layout()

    line_img_io = io.BytesIO()
    plt.savefig(line_img_io, format='png')
    line_img_io.seek(0)
    line_img_base64 = base64.b64encode(line_img_io.getvalue()).decode()
    plt.close()

    return pie_img_base64, line_img_base64
