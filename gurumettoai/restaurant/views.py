from django.shortcuts import render
from django.http import JsonResponse
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

        # ユーザーのメッセージからジャンルを特定
        genre_code = None
        for genre, code in GENRE_CODES.items():
            if genre in user_message:
                genre_code = code
                break

        # 座敷や個室の条件を解析
        keyword_conditions = []
        if "座敷" in user_message:
            keyword_conditions.append("座敷")
        if "個室" in user_message:
            keyword_conditions.append("個室")
        if "wifi" in user_message:
            keyword_conditions.append("wifi")
        if "コース" in user_message:
            keyword_conditions.append("コース")
        if "飲み放題" in user_message:
            keyword_conditions.append("飲み放題")
        if "食べ放題" in user_message:
            keyword_conditions.append("食べ放題")
        if "掘りごたつ" in user_message:
            keyword_conditions.append("掘りごたつ")
        if "カード可" in user_message:
            keyword_conditions.append("カード可")
        if "禁煙" in user_message:
            keyword_conditions.append("禁煙")
        if "喫煙" in user_message:
            keyword_conditions.append("喫煙")
        if "駐車場" in user_message:
            keyword_conditions.append("駐車場")
        if "深夜" in user_message:
            keyword_conditions.append("midnight")
        if "赤羽" in user_message:
            keyword_conditions.append("赤羽")
        if "渋谷" in user_message:
            keyword_conditions.append("渋谷")
        if "新宿" in user_message:
            keyword_conditions.append("新宿")
        if "池袋" in user_message:
            keyword_conditions.append("池袋")

        # キーワードパラメータを生成（カンマ区切り）
        keyword_param = ",".join(keyword_conditions) if keyword_conditions else None

        # ジャンルが特定できなかった場合
        if not genre_code and not keyword_param:
            return JsonResponse({'response': "該当するジャンルや条件が見つかりませんでした。例: ラーメン、居酒屋、座敷あり、個室あり"})

        # 飲食店の推薦データを取得
        recommendations = get_restaurant_recommendations(genre_code=genre_code, keyword=keyword_param)
        if recommendations:
            response_html = ""
            for rec in recommendations:
                response_html += f"""
                <div>
                    <h3>{rec['name']}</h3>
                    <p>住所: {rec['address']}</p>
                    <p> {rec['catch']}</p>
                    <a href="{rec['url']}" target="_blank">詳細はこちら</a>
                    <img src="{rec['image_url']}" alt="{rec['name']}" style="width:200px; height:auto;">
                    <button class="like-button">いいね！</button>
                </div>
                <br>
                """
            return JsonResponse({'response': response_html})
        else:
            return JsonResponse({'response': "該当する店舗が見つかりませんでした。"})
    return JsonResponse({'response': "無効なリクエストです。"})


# HotPepper APIでレストラン情報を取得
import random  # ランダム要素を追加するためにインポート

# HotPepper APIでレストラン情報を取得
def get_restaurant_recommendations(genre_code=None, keyword=None):
    api_key = os.getenv('HOTPEPPER_API_KEY')
    url = 'http://webservice.recruit.co.jp/hotpepper/gourmet/v1/'
    params = {
        'key': api_key,
        'format': 'json',
        'keyword': "赤羽",  # デフォルトエリア
        'large_area': 'Z011',  # 東京エリア
        'count': 50  #APIの最大値である50件
    }
    if genre_code:
        params['genre'] = genre_code
    if keyword:
        params['keyword'] = keyword

    response = requests.get(url, params=params)
    if response.status_code == 200:
        shops = response.json().get('results', {}).get('shop', [])
        
        # 50件からランダムで5個抽出
        if len(shops) > 5:
            shops = random.sample(shops, 5)

        return [
            {
                'name': shop.get('name'),
                'address': shop.get('address'),
                'catch': shop.get('catch'),  # キャッチコピーを追加
                'url': shop.get('urls', {}).get('pc'),
                'image_url': shop.get('photo', {}).get('pc', {}).get('l')
                
            }
            for shop in shops
        ]
    return []