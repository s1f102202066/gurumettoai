from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import requests

# APIのベースURLとAPIキー
OPENAI_API_BASE = "https://api.openai.iniad.org/api/v1"
API_KEY = "IrwRn99zrmmNcOtw0Kh3_XTJFiA3JmKsI-XLO9_TLROXsZRThQTAhsEcEt9IsVgGBRoUGkwcCtSTFrkyMlT2NJQ"

def home(request):
    """
    トップページを表示する
    """
    return render(request, 'restaurant/index.html')

@csrf_exempt
def chat(request):
    """
    ユーザーのメッセージを受け取り、Chat Completion APIを使用して応答を生成
    """
    if request.method != 'POST':
        return JsonResponse({'response': "無効なリクエストです。"})

    user_message = request.POST.get('message', '').strip()

    # Chat Completion APIを使用して応答を生成
    try:
        chatgpt_response = call_chat_completion_api(user_message)
        return JsonResponse({'response': chatgpt_response})
    except Exception as e:
        return JsonResponse({'response': f"エラーが発生しました: {str(e)}"})

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


def review(request, shop_id):
    """
    お店の詳細情報を表示する
    """
    # サンプルデータ（仮データとして使用、実際はAPIやデータベースから取得）
    sample_shops = {
        "1": {
            "name": "ラーメン屋一番",
            "address": "東京都渋谷区1-2-3",
            "url": "https://example.com/shop1",
            "image_url": "https://via.placeholder.com/800x400?text=Shop+Image+1"
        },
        "2": {
            "name": "居酒屋たろう",
            "address": "東京都新宿区4-5-6",
            "url": "https://example.com/shop2",
            "image_url": "https://via.placeholder.com/800x400?text=Shop+Image+2"
        }
    }

    # お店の詳細を取得
    shop = sample_shops.get(shop_id, None)
    if not shop:
        return JsonResponse({'error': 'お店が見つかりませんでした。'}, status=404)

    # テンプレートにデータを渡してレンダリング
    return render(request, 'restaurant/review.html', {'shop': shop})
