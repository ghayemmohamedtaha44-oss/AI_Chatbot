import json
import requests
import openai
import time
import re

# ============================================================
#  تنظیمات ربات بله
# ============================================================
TOKEN = "1097661845:chidj5aZzJc_lVXb4Q-zruMVQyYvbAAAHH4"
BASE_URL = f"https://tapi.bale.ai/{TOKEN}"

# ============================================================
#  تنظیمات اولاما
# ============================================================
OLLAMA_BASE_URL = "http://office.sadidafarin.ir:11434/v1/"
OLLAMA_API_KEY = "ollama"
MODEL_NAME = "llama3.2:latest"   # در صورت نیاز تغییر دهید

TEMPERATURE = 0.3
MAX_TOKENS = 500
TOP_P = 0.9

# دستورالعمل سیستم به انگلیسی (پاسخ‌ها فقط انگلیسی)
SYSTEM_PROMPT = (
    "You are an AI assistant that responds **only in English**. "
    "Do not use Persian, Arabic, Hindi, or any other language under any circumstances. "
    "Even if the user asks in another language, you must reply in English. "
    "Keep your answers clear, concise, and grammatically correct. "
    "If you don't know the answer, honestly say 'I don't know'."
)

client = openai.OpenAI(
    base_url=OLLAMA_BASE_URL,
    api_key=OLLAMA_API_KEY,
)

conversation_histories = {}

# ============================================================
#  توابع کمکی
# ============================================================

def clean_text(text: str) -> str:
    """
    پاکسازی متن: تبدیل حروف عربی به فارسی (در صورت نیاز) و حذف فاصله‌های اضافی
    (حروف انگلیسی نگهداری می‌شوند)
    """
    # تبدیل حروف عربی به فارسی (اختیاری)
    arabic_to_persian = {
        'ي': 'ی',
        'ك': 'ک',
        'ة': 'ه',
        '‍': '',
    }
    for ar, fa in arabic_to_persian.items():
        text = text.replace(ar, fa)
    # حذف فاصله‌های اضافی (بیش از یک فاصله)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def get_last_update():
    method = "getUpdates"
    url = f"{BASE_URL}/{method}"
    params = {"limit": 100, "timeout": 5}
    try:
        resp = requests.get(url, params=params, timeout=10)
    except requests.exceptions.RequestException as e:
        print(f"❌ Error connecting to Bale: {e}")
        return None, None, None, None, None
    if resp.status_code != 200:
        print(f"❌ Error receiving messages: {resp.status_code}")
        return None, None, None, None, None
    data = resp.json()
    results = data.get('result', [])
    if not results:
        return None, None, None, None, None
    last_update = results[-1]
    update_id = last_update.get('update_id')
    message = last_update.get('message', {})
    chat_id = message.get('chat', {}).get('id')
    text = message.get('text')
    username = message.get('from', {}).get('username')
    return update_id, chat_id, text, username, results

def send_message_to_user(chat_id, reply_text):
    method = "sendMessage"
    url = f"{BASE_URL}/{method}"
    max_len = 4000
    if len(reply_text) <= max_len:
        payload = {"chat_id": chat_id, "text": reply_text}
        try:
            resp = requests.post(url, json=payload, timeout=10)
            return resp.status_code == 200
        except requests.exceptions.RequestException:
            return False
    parts = [reply_text[i:i+max_len] for i in range(0, len(reply_text), max_len)]
    success = True
    for part in parts:
        payload = {"chat_id": chat_id, "text": part}
        try:
            resp = requests.post(url, json=payload, timeout=10)
            if resp.status_code != 200:
                success = False
        except requests.exceptions.RequestException:
            success = False
    return success

def confirm_updates(all_updates):
    if not all_updates:
        return
    max_id = max([u.get('update_id') for u in all_updates if u.get('update_id') is not None])
    method = "getUpdates"
    url = f"{BASE_URL}/{method}"
    params = {"offset": max_id + 1, "limit": 0}
    try:
        requests.get(url, params=params, timeout=5)
    except requests.exceptions.RequestException:
        pass

def send_prompt_stream(messages: list):
    try:
        stream = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
            top_p=TOP_P,
            stream=True,
            timeout=30.0,
        )
        for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content
    except openai.APIConnectionError:
        yield "❌ Error: Could not connect to Ollama server."
    except openai.APITimeoutError:
        yield "❌ Error: Request timed out."
    except Exception as e:
        yield f"❌ Unknown error: {e}"

def get_full_response(messages: list) -> str:
    full_response = ""
    for chunk in send_prompt_stream(messages):
        full_response += chunk
        if len(full_response) > 3000:
            full_response += "\n... [continued in next message]"
            break
    if full_response.strip():
        full_response = clean_text(full_response)
    else:
        full_response = "No response received. Please try again."
    return full_response

# ============================================================
#  حلقه اصلی (اجرای مداوم)
# ============================================================

if __name__ == "__main__":
    print("🤖 Bale bot + Ollama (English only) started...")
    print("⏳ Waiting for new messages...\n")
    while True:
        try:
            update_id, chat_id, user_text, username, all_updates = get_last_update()
            if chat_id and user_text:
                print(f"📩 New message from @{username}: {user_text}")
                if chat_id not in conversation_histories:
                    conversation_histories[chat_id] = [
                        {"role": "system", "content": SYSTEM_PROMPT}
                    ]
                conversation_histories[chat_id].append({"role": "user", "content": user_text})
                print("⏳ Getting response from Ollama...")
                reply_text = get_full_response(conversation_histories[chat_id])
                conversation_histories[chat_id].append({"role": "assistant", "content": reply_text})
                if len(conversation_histories[chat_id]) > 4:
                    system_msg = conversation_histories[chat_id][0]
                    conversation_histories[chat_id] = [system_msg] + conversation_histories[chat_id][-3:]
                if send_message_to_user(chat_id, reply_text):
                    print("✅ Response sent successfully.")
                else:
                    print("❌ Failed to send response.")
                confirm_updates(all_updates)
                print(f"✅ {len(all_updates)} messages confirmed.\n")
            else:
                pass
            time.sleep(2)
        except KeyboardInterrupt:
            print("\n🛑 Bot stopped by user.")
            break
        except Exception as e:
            print(f"❌ Unexpected error in main loop: {e}")
            time.sleep(5)