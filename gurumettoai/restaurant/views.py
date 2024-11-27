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

def fetch_reviews(restaurant_name):
    """
    Google Places APIを使って、指定された飲食店の口コミを取得する
    """
    api_key = os.getenv('GOOGLE_MAPS_API_KEY')

    # 場所の検索エンドポイント
    search_url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
    search_params = {
        'input': restaurant_name,
        'inputtype': 'textquery',
        'fields': 'place_id',
        'key': api_key
    }
    search_response = requests.get(search_url, params=search_params)
    search_data = search_response.json()

    if 'candidates' in search_data and len(search_data['candidates']) > 0:
        place_id = search_data['candidates'][0]['place_id']
    else:
        return {"error": f"No details found for {restaurant_name}"}

    # 場所の詳細エンドポイント
    details_url = "https://maps.googleapis.com/maps/api/place/details/json"
    details_params = {
        'place_id': place_id,
        'fields': 'name,rating,reviews',
        'key': api_key
    }
    details_response = requests.get(details_url, params=details_params)
    details_data = details_response.json()

    return details_data.get('result', {})

def suggest_restaurant_with_reviews(request):
    """
    AIが提案した飲食店情報に基づいて口コミを取得し、返す
    """
    # 例: AIが提案する飲食店名 (ここは後でAIから生成されるように接続)
    suggested_restaurant = "スターバックス"
    restaurant_details = fetch_reviews(suggested_restaurant)

    if "error" in restaurant_details:
        return JsonResponse({"error": restaurant_details["error"]}, status=404)

    return JsonResponse({
        "suggested_restaurant": suggested_restaurant,
        "details": restaurant_details
    })