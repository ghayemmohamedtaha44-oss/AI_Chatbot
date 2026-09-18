import json
import requests
import openai
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from middlewares import add_essentials
import uvicorn

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

# SYSTEM PROMPT (English only)
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
#  ساخت اپلیکیشن FastAPI
# ============================================================
app = FastAPI(title="Bale Bot + AI API", version="1.0.0")

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
#  Bale Robot Methods
# ============================================================
def get_ai_response(messages: list) -> str:
    """ارسال پیام‌ها به اولاما و دریافت پاسخ (بدون استریم)"""
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
            top_p=TOP_P,
            stream=False,
            timeout=30.0,
        )
        reply = response.choices[0].message.content
        return reply if reply else "No response received."
    except openai.APIConnectionError:
        return "❌ Error: Could not connect to Ollama server."
    except openai.APITimeoutError:
        return "❌ Error: Request timed out."
    except Exception as e:
        return f"❌ Unknown error: {e}"


def send_message_to_user(chat_id, reply_text):
    """ارسال پیام به کاربر در بله"""
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


# ============================================================
#  FastAPI Endpoints
# ============================================================

@app.post("/baleai")
async def bale_ai(update: Request):
    # convert update object from byte to string
    resp = (await update.body()).decode('utf8').replace("'", '"')
    # convert resp string to dictionary
    resp = json.loads(resp)

    # extract text and chat id from resp
    user_text = resp["message"]["text"]
    chat_id = resp["message"]["chat"]["id"]

    # create messages object to send to ai
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_text}
    ]

    # send request to ai and get the response 
    ai_reply = get_ai_response(messages)

    # send the ai reply to bale user and get the result(true/false)
    result = send_message_to_user(chat_id, ai_reply)

    final_result = {"bale_status": result, "ai_reply": ai_reply}
    print(final_result)
 
    return final_result


# ============================================================
#  اجرا (با uvicorn)
# ============================================================

if __name__ == "__main__":
    # اجرای ربات بله در یک ترد جداگانه
    # bot_thread = threading.Thread(target=run_bot, daemon=True)
    # bot_thread.start()
    
    # اجرای FastAPI با uvicorn
    print("🌐 Starting FastAPI server on http://0.0.0.0:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)