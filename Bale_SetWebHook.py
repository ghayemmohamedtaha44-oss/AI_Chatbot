import requests

TOKEN = "1097661845:chidj5aZzJc_lVXb4Q-zruMVQyYvbAAAHH4"
BASE_URL = f"https://tapi.bale.ai/{TOKEN}"



def set_webhook():
    # Set bale webhook url
    method = "setWebhook"
    url = f"{BASE_URL}/{method}"
    payload = {"url": "https://webhook.site/7a099191-b6a8-4ee0-af51-e1ac1ebd42a8"}
    resp = requests.post(url, json=payload, timeout=10)
    print(resp.status_code)

def check_webhook():
    # Check webhook url
    method = "getWebhookInfo"
    url2 = f"{BASE_URL}/{method}"
    resp2 = requests.get(url2)
    resp2.status_code
    print(resp2.text)



if __name__ == "__main__":
    set_webhook()
    check_webhook()