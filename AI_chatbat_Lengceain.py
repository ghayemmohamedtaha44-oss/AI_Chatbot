from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
import sys

# ===== تنظیمات کلاینت برای اتصال به اولاما =====
BASE_URL = "http://office.sadidafarin.ir:11434"
MODEL_NAME = "llama3.2:latest"

# ایجاد کلاینت ChatOllama
model = ChatOllama(
    model=MODEL_NAME,
    base_url=BASE_URL,
    temperature=0.7,
)


def send_prompt_stream(messages: list):
    """
    ارسال لیست پیام‌ها (تاریخچه مکالمه) به مدل و دریافت پاسخ به صورت Streaming
    messages: لیستی از دیکشنری‌های {'role': 'user'/'assistant', 'content': '...'}
    """
    try:
        # تبدیل messages به فرمت LangChain
        lc_messages = []
        for msg in messages:
            if msg["role"] == "user":
                lc_messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                lc_messages.append(AIMessage(content=msg["content"]))

        # ارسال درخواست با stream=True
        for chunk in model.stream(lc_messages):
            # هر تیکه‌ای که می‌رسه رو yield کن
            if chunk.content:
                yield chunk.content

    except Exception as e:
        yield f"❌ Unknown error: {e}"


def main():
    print("🤖 Chatbot with Ollama (via LangChain - Streaming mode)")
    print(f"Model: {MODEL_NAME}")
    print("Enter 'exit' or 'quit' to quit.")
    print("-" * 50)

    # تاریخچه مکالمه به صورت لیستی از دیکشنری‌ها
    messages = []

    while True:
        user_input = input("\n👤 You: ").strip()

        if user_input.lower() in ("exit", "quit", "خروج"):
            print("👋 Goodbye!")
            break

        if not user_input:
            continue

        # اضافه کردن پیام کاربر به تاریخچه
        messages.append({"role": "user", "content": user_input})

        # نمایش برچسب ربات
        print("🤖 Bot: ", end="", flush=True)

        # دریافت پاسخ به صورت Streaming
        full_response = ""
        try:
            for chunk in send_prompt_stream(messages):
                sys.stdout.write(chunk)
                sys.stdout.flush()
                full_response += chunk
            print()  # بعد از تموم شدن پاسخ، یه خط جدید بزن
        except Exception as e:
            print(f"\n❌ Error in streaming: {e}")
            continue

        # اضافه کردن پاسخ کامل ربات به تاریخچه
        if full_response:
            messages.append({"role": "assistant", "content": full_response})
        else:
            messages.append({"role": "assistant", "content": "❌ No response received."})


if __name__ == "__main__":
    main()