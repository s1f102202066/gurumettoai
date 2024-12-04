from django.shortcuts import render
from django.http import JsonResponse
from .models import Restaurant
import openai
import requests
import os
from dotenv import load_dotenv
from django.views.decorators.csrf import csrf_exempt

# 環境変数の読み込み
load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

def home(request):
    return render(request, 'restaurant/index.html')

# HotPepper APIを使ったレストラン情報取得
def get_restaurant_recommendations(query, genre=None):
    api_key = os.getenv('HOTPEPPER_API_KEY')
    url = 'http://webservice.recruit.co.jp/hotpepper/gourmet/v1/'
    params = {
        'key': api_key,
        'format': 'json',
        'keyword': "赤羽",  # 赤羽エリアをデフォルト設定
        'large_area': 'Z011',  # 東京エリア
        'count': 5
    }

    # ジャンルコードを追加（オプション）
    if genre:
        params['genre'] = genre

    response = requests.get(url, params=params)
    if response.status_code == 200:
        results = response.json().get('results', {}).get('shop', [])
        recommendations = []
        for shop in results:
            recommendations.append({
                'name': shop.get('name'),
                'address': shop.get('address'),
                'url': shop.get('urls', {}).get('pc'),
                'image_url': shop.get('photo', {}).get('pc', {}).get('l')
            })
        return recommendations
    else:
        return []

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

@csrf_exempt
def chat(request):
    if request.method == 'POST':
        user_message = request.POST.get('message', '').strip()

        # 飲食に関連するキーワードが含まれているかをチェック
        keywords = list(GENRE_CODES.keys())
        is_related_to_food = any(keyword in user_message for keyword in keywords)

        if not is_related_to_food:
            return JsonResponse({'response': "お探しの飲食店の条件を入力してください。"})

        # ユーザーのメッセージからジャンルを特定
        selected_genre = None
        for genre, genre_code in GENRE_CODES.items():
            if genre in user_message:
                selected_genre = genre_code
                break

        # レストランの推薦を取得（赤羽固定、ジャンルがあれば適用）
        recommendations = get_restaurant_recommendations(user_message, genre=selected_genre)
        if recommendations:
            recommendation_text = ""
            for rec in recommendations:
                recommendation_text += (
                    f"- 店名: {rec['name']} | "
                    f"住所: {rec['address']} | "
                    f"詳細: {rec['url']} | "
                    f"画像: {rec['image_url']}\n"
                )
        else:
            recommendation_text = "赤羽エリアで該当する店舗が見つかりませんでした。ほかのジャンルもお試しください！"

        # 飲食店情報のみを返す
        return JsonResponse({'response': recommendation_text})

    return JsonResponse({'response': "無効なリクエストです。"})
