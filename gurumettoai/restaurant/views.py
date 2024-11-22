from django.shortcuts import render
from django.http import JsonResponse
from .models import Restaurant
import openai
import requests
import os
from dotenv import load_dotenv
from django.views.decorators.csrf import csrf_exempt

load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

def home(request):
    return render(request, 'restaurant/index.html')

def get_restaurant_recommendations(query):
    api_key = os.getenv('HOTPEPPER_API_KEY')
    url = 'http://webservice.recruit.co.jp/hotpepper/gourmet/v1/'
    params = {
        'key': api_key,
        'format': 'json',
        'keyword': query,
        'large_area': 'Z011',  # 東京エリアを指定
        'count': 5
    }
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
@csrf_exempt
def chat(request):
    if request.method == 'POST':
        user_message = request.POST.get('message', '')

        # OpenAIの応答を生成
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant. No matter the topic, you always relate the conversation back to restaurants or food recommendations."},
                {"role": "user", "content": user_message}
            ],
            max_tokens=1000
        )

        chatgpt_response = response['choices'][0]['message']['content'].strip()

        # レストランの推薦を追加
        recommendations = get_restaurant_recommendations(user_message)
        if recommendations:
            recommendation_text = ""
            for rec in recommendations:
                recommendation_text += f"- 店名: {rec['name']}\n  住所: {rec['address']}\n  詳細: {rec['url']}\n  画像: {rec['image_url']}\n\n"
            chatgpt_response += "\n\n" + recommendation_text.strip()
        else:
            chatgpt_response += "\n\nところで、美味しい飲食店をお探しではありませんか？どんな話題でも食事に関する情報をご提供いたします。"

        return JsonResponse({'response': chatgpt_response})
