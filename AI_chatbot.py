import openai
import sys

# ===== تنظیمات کلاینت برای اتصال به اولاما =====
BASE_URL = "http://office.sadidafarin.ir:11434/v1/"
API_KEY = "ollama"
MODEL_NAME = "llama3.2:latest"

# ایجاد کلاینت OpenAI
client = openai.OpenAI(
    base_url=BASE_URL,
    api_key=API_KEY,
)


def send_prompt_stream(messages: list):
    """
    ارسال درخواست به مدل و دریافت پاسخ به صورت Streaming (حرف‌به‌حرف)
    این تابع یک Generator (تولیدکننده) هست که هر تیکه از پاسخ رو به مرور برمی‌گردونه
    """
    try:
        # ارسال درخواست با stream=True
        stream = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=0.7,
            stream=True,  # فعال کردن حالت streaming
        )

        # اینجا هر تیکه‌ای که از اولاما می‌رسه رو به مرور برمی‌گردونیم
        for chunk in stream:
            # توی هر chunk ممکنه محتوا وجود داشته باشه یا نه
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content
            else:
                # اگه chunk آخر بود و محتوایی نداشت، حلقه تموم می‌شه
                continue

    except openai.APIConnectionError:
        yield "❌ Error: Could not connect to Ollama server. Make sure Ollama is running."
    except openai.APITimeoutError:
        yield "❌ Error: Request timeout."
    except Exception as e:
        yield f"❌ Unknown error: {e}"


def main():
    print("🤖 Chatbot with Ollama (Streaming mode)")
    print(f"Model: {MODEL_NAME}")
    print("Enter 'exit' or 'quit' to quit.")
    print("-" * 50)

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
            # اینجا تیکه‌های پاسخ یکی‌یکی میان
            for chunk in send_prompt_stream(messages):
                # هر تیکه رو همون لحظه چاپ کن
                sys.stdout.write(chunk)
                sys.stdout.flush()
                full_response += chunk  # تیکه‌ها رو جمع کن تا کامل بشه
            print()  # بعد از تموم شدن پاسخ، یه خط جدید بزن
        except Exception as e:
            print(f"\n❌ Error in streaming: {e}")
            continue

        # اضافه کردن پاسخ کامل ربات به تاریخچه
        if full_response:
            messages.append({"role": "assistant", "content": full_response})
        else:
            # اگه پاسخی نیومد، یه پیام پیش‌فرض بذار
            messages.append({"role": "assistant", "content": "❌ No response received."})


if __name__ == "__main__":
    main()