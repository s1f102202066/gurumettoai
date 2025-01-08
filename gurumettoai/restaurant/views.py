from django.shortcuts import render
from django.http import JsonResponse
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
def get_restaurant_recommendations(genre=None):
    api_key = os.getenv('HOTPEPPER_API_KEY')
    if api_key is None:
        return {'response': 'APIキーが設定されていません。'}

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

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
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
    except requests.exceptions.RequestException as e:
        return {'response': f"APIアクセス中にエラーが発生しました: {str(e)}"}

# ジャンルコードの辞書
GENRE_CODES = {
    "ラーメン": "G013",
    "居酒屋": "G001",
    "カフェ・スイーツ": "G014",
    "ダイニングバー・バル": "G002",
    "創作料理": "G003",
    "和食": "G004",
    "洋食": "G005",
    "イタリアン・フレンチ": "G006",
    "中華": "G007",
    "焼肉": "G008",
    "韓国料理": "G017",
    "アジア・エスニック料理": "G009",
    "各国料理": "G010",
    "カラオケ・パーティ": "G011",
    "バー・カクテル": "G012",
    "お好み焼き・もんじゃ": "G016",
    "その他グルメ": "G015"
}

@csrf_exempt
def chat(request):
    if request.method == 'POST':
        user_message = request.POST.get('message', '').strip()

        # ChatGPTで条件を解析
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "あなたは日本語で応答する飲食店アシスタントです。ユーザーの入力から、必要な情報（ジャンル）を抽出し、それを基に赤羽のレストランを探すのに必要なデータを返してください。",
                },
                {"role": "user", "content": user_message}
            ],
            max_tokens=1000,
        )

        # ChatGPTの応答からジャンルを抽出
        parsed_response = response['choices'][0]['message']['content'].strip()
        genre = None

        # ChatGPT応答からジャンルを簡易解析（例: ジャンル: ラーメン）
        if "ジャンル" in parsed_response:
            genre_text = parsed_response.split("ジャンル:")[1].split(",")[0].strip()
            genre = GENRE_CODES.get(genre_text)

        # 飲食店情報をHotPepper APIから取得
        recommendations = get_restaurant_recommendations(genre=genre)
        if recommendations:
            if isinstance(recommendations, dict):  # エラー時は辞書を返す
                return JsonResponse(recommendations)

            recommendation_text = "お探しの条件に合った飲食店はこちらです:\n"
            for rec in recommendations:
                recommendation_text += (
                    f"- <a href='{rec['url']}' target='_blank'>{rec['name']}</a> | "
                    f"住所: {rec['address']} | "
                    f"<img src='{rec['image_url']}' alt='{rec['name']}' style='max-height:100px;' />\n"
                )
        else:
            recommendation_text = "赤羽エリアで該当する店舗が見つかりませんでした。ほかの条件でもお試しください！"

        return JsonResponse({'response': recommendation_text})

    return JsonResponse({'response': "無効なリクエストです。"})
