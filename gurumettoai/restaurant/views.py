from django.shortcuts import render
from django.http import JsonResponse
from .models import Restaurant
import openai
import requests
import os
from dotenv import load_dotenv
from django.views.decorators.csrf import csrf_exempt

from django.shortcuts import render

def home(request):
    return render(request, 'restaurant/index.html')  # フォルダ構造を考慮したパスを指定  # 適切なテンプレートファイル名を指定

# ジャンルコードの辞書
GENRE_CODES = {
    "ラーメン": "G013",
    "居酒屋": "G001",
    "カフェ・スイーツ": "G014",
    "ダイニングバー・バル":"G002",
    "創作料理":"G003",
    "和食":"G004",
    "洋食":"G005",
    "イタリアン・フレンチ":"G006",
    "中華":"G007",
    "焼肉":"G008",
    "韓国料理":"G017",
    "アジア・エスニック料理":"G009",
    "各国料理":"G010",
    "カラオケ・パーティ":"G011",
    "バー・カクテル":"G012",
    "お好み焼き・もんじゃ":"G016",
    "その他グルメ":"G015"

}


# HotPepper APIでレストラン情報を取得
def get_restaurant_recommendations(genre_code=None):
    api_key = os.getenv('HOTPEPPER_API_KEY')
    url = 'http://webservice.recruit.co.jp/hotpepper/gourmet/v1/'
    params = {
        'key': api_key,
        'format': 'json',
        'keyword': "赤羽",  # 赤羽エリアをデフォルト設定
        'large_area': 'Z011',  # 東京エリア
        'count': 5
    }
    if genre_code:
        params['genre'] = genre_code

    response = requests.get(url, params=params)
    if response.status_code == 200:
        shops = response.json().get('results', {}).get('shop', [])
        return [
            {
                'name': shop.get('name'),
                'address': shop.get('address'),
                'url': shop.get('urls', {}).get('pc'),
                'image_url': shop.get('photo', {}).get('pc', {}).get('l')
            }
            for shop in shops
        ]
    return []

@csrf_exempt
def chat(request):
    if request.method == 'POST':
        user_message = request.POST.get('message', '').strip()

        # ユーザーのメッセージからジャンルを特定
        genre_code = None
        for genre, code in GENRE_CODES.items():
            if genre in user_message:
                genre_code = code
                break

        # ジャンルが特定できなかった場合
        if not genre_code:
            return JsonResponse({'response': "該当するジャンルが見つかりませんでした。例: ラーメン、居酒屋"})

        # 飲食店の推薦データを取得
        recommendations = get_restaurant_recommendations(genre_code=genre_code)
        if recommendations:
            response_html = ""
            for rec in recommendations:
                response_html += f"""
                <div>
                    <h3>{rec['name']}</h3>
                    <p>住所: {rec['address']}</p>
                    <a href="{rec['url']}" target="_blank">詳細はこちら</a>
                    <img src="{rec['image_url']}" alt="{rec['name']}" style="width:200px; height:auto;">
                </div>
                <br>
                """
            return JsonResponse({'response': response_html})
        else:
            return JsonResponse({'response': "該当する店舗が見つかりませんでした。"})
    return JsonResponse({'response': "無効なリクエストです。"})