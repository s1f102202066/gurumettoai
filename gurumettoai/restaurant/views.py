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
    "カフェ": "G014",
    # 必要に応じてジャンルを追加
}

@csrf_exempt
def chat(request):
    if request.method == 'POST':
        user_message = request.POST.get('message', '').strip()

        # ユーザーのメッセージからジャンルを特定
        selected_genre = None
        for genre, genre_code in GENRE_CODES.items():
            if genre in user_message:
                selected_genre = genre_code
                break

        # OpenAIの応答を生成
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "あなたは日本語で応答する飲食店アシスタントです。どんな入力でも日本語で返答し、赤羽にあるレストランの情報を提供してください。"},
                {"role": "user", "content": user_message}
            ],
            max_tokens=1000
        )

        chatgpt_response = response['choices'][0]['message']['content'].strip()

        # レストランの推薦を追加（赤羽固定、ジャンルがあれば適用）
        recommendations = get_restaurant_recommendations(user_message, genre=selected_genre)
        if recommendations:
            recommendation_text = ""
            for rec in recommendations:
                recommendation_text += f"- 店名: {rec['name']} 住所: {rec['address']} 詳細: {rec['url']} {rec['image_url']}  {rec['name']} "
            chatgpt_response += "赤羽エリアのおすすめ飲食店:" + recommendation_text.strip()
        else:
            chatgpt_response += "赤羽エリアで該当する店舗が見つかりませんでした。ほかのジャンルもお試しください！"

        return JsonResponse({'response': chatgpt_response})

    return JsonResponse({'response': "無効なリクエストです。"})


