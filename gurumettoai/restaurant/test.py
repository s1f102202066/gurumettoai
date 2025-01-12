import requests

def check_api_key(api_key, base_url="https://api.openai.iniad.org/api/v1"):
    """APIキーが有効かどうかを確認する関数"""
    try:
        # Chat Completion API に対してテストリクエストを送信
        endpoint = f"{base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        data = {
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "system", "content": "Hello, this is a test message."}],
        }

        # APIリクエストを送信
        response = requests.post(endpoint, headers=headers, json=data)

        # ステータスコードをチェック
        if response.status_code == 200:
            print("APIキーは有効です！")
            print("応答内容:", response.json())
            return True
        elif response.status_code == 401:
            print("エラー: 無効なAPIキーです。")
            return False
        else:
            print(f"エラー: ステータスコード {response.status_code} が返されました。")
            print("応答内容:", response.json())
            return False
    except Exception as e:
        print(f"予期しないエラーが発生しました: {e}")
        return False

if __name__ == "__main__":
    # 確認するAPIキーを入力
    api_key = input("確認するOpenAI APIキーを入力してください: ")

    # APIキーの検証
    is_valid = check_api_key(api_key)

    if not is_valid:
        print("APIキーを確認して、再試行してください。")
    else:
        print("APIキーは正しく動作しています。")
