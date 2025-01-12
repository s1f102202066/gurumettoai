from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import requests
import openai
import requests

# APIのベースURLとAPIキー
OPENAI_API_BASE = "https://api.openai.iniad.org/api/v1"
API_KEY = "IrwRn99zrmmNcOtw0Kh3_XTJFiA3JmKsI-XLO9_TLROXsZRThQTAhsEcEt9IsVgGBRoUGkwcCtSTFrkyMlT2NJQ"
GOOGLE_MAPS_API_KEY = "AIzaSyDkwReNUSpd7TVjPZGI2hBkfPk51mqxAnE"
GOOGLE_API_KEY = "AIzaSyDkwReNUSpd7TVjPZGI2hBkfPk51mqxAnE"

def home(request):
    """
    トップページを表示する
    """
    return render(request, 'restaurant/index.html')

@csrf_exempt
def chat(request):
    """
    チャットリクエストを処理し、Googleから取得したレビューを表示。
    """
    if request.method != 'POST':
        return JsonResponse({'response': "無効なリクエストです。"})

    user_message = request.POST.get('message', '').strip()

    # サンプルデータ（実際にはGoogle Places APIで取得）
    sample_shops = [
        {
            "place_id": "ChIJN1t_tDeuEmsRUsoyG83frY4",  # Google Place ID
            "name": "ラーメン屋一番",
            "station": "渋谷駅",
            "budget": "1000〜1500円"
        },
        {
            "place_id": "ChIJLfySpTOuEmsRsc_JfJtljdc",
            "name": "居酒屋たろう",
            "station": "新宿駅",
            "budget": "3000〜5000円"
        }
    ]

    response_list = []
    for shop in sample_shops[:3]:
        # Google Places APIからレビューを取得
        details = get_place_details(shop["place_id"])

        if not details:
            continue

        # 各お店の情報をHTML形式で生成
        response_list.append(
            f"""
            <div class="shop-card">
                <a href="/review/{shop['place_id']}/">{shop['name']}</a>
                <p>{details['summary']}</p>
                <p><strong>星:</strong> {details['rating']} / 5 ({details['review_count']}件)</p>
                <p><strong>最寄り駅:</strong> {shop['station']}</p>
                <p><strong>予算:</strong> {shop['budget']}</p>
            </div>
            """
        )

    return JsonResponse({'response': response_list})


def call_chat_completion_api(user_message):
    url = f"{OPENAI_API_BASE}/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "gpt-4",
        "messages": [
            {"role": "system", "content": "あなたは飲食店を探すAIアシスタントです。"},
            {"role": "user", "content": user_message}
        ],
        "max_tokens": 500,  # 最大トークン数を増加
        "temperature": 0.7
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        data = response.json()
        return data["choices"][0]["message"]["content"].strip()
    else:
        raise Exception(f"APIリクエストが失敗しました: {response.status_code} {response.text}")


def review(request, place_id):
    """
    お店の詳細情報を表示し、所要時間を計算。
    """
    origin = "35.6895,139.6917"  # 現在地の緯度・経度（例: 東京駅）
    destination = place_id  # Google Place ID

    duration = get_travel_time(origin, destination)

    return render(request, 'restaurant/review.html', {'duration': duration})


def summarize_reviews(reviews):
    """
    レビューを要約し、100字以内のテキストを生成。
    """
    if not reviews:
        return "レビュー情報はありません。"
    joined_reviews = " ".join(reviews)
    return (joined_reviews[:97] + "...") if len(joined_reviews) > 100 else joined_reviews

def get_place_details(place_id):
    """
    Google Places APIを使用して場所の詳細を取得し、レビューを要約。
    """
    url = f"https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        "place_id": place_id,
        "fields": "rating,user_ratings_total,reviews",
        "key": GOOGLE_API_KEY
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json().get("result", {})
        if not data:
            return None

        reviews = data.get("reviews", [])
        summary = summarize_reviews([review["text"] for review in reviews])

        return {
            "rating": data.get("rating", "N/A"),
            "review_count": data.get("user_ratings_total", 0),
            "summary": summary
        }
    return None

def get_travel_time(origin, destination):
    """
    Google Distance Matrix APIで所要時間を取得。
    """
    url = f"https://maps.googleapis.com/maps/api/distancematrix/json"
    params = {
        "origins": origin,
        "destinations": f"place_id:{destination}",
        "key": GOOGLE_API_KEY
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        rows = data.get("rows", [])
        if rows:
            elements = rows[0].get("elements", [])
            if elements:
                element = elements[0]
                if element.get("status") == "OK" and "duration" in element:
                    return element["duration"]["text"]

    return "所要時間が取得できませんでした。"