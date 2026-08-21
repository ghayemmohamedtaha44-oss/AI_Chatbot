from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer
from chatterbot.trainers import ChatterBotCorpusTrainer

# اول یه ربات چت میسازیم
# read_only=True باعث میشه ربات فقط جواب بده و چیز جدیدی یاد نگیره
# logic_adapters مشخص میکنه که ربات چطوری جواب پیدا کنه
# default_adapter='chatterbot.logic.BestMatch' یعنی بهترین تطابق رو از بین جواب‌های یادگرفته شده پیدا کنه
chatbot = ChatBot(
    'HooshangBot',
    read_only=False,
    logic_adapters=[
        {
            'import_path': 'chatterbot.logic.BestMatch',
            'default_response': 'متاسفم، متوجه نشدم. میتونی منظورت رو واضح تر بگی؟',
            'maximum_similarity_threshold': 0.90 # هرچی این عدد بالاتر باشه، ربات سخت تر جواب میده ولی جواب‌ها دقیق‌تر میشن
        }
    ]
)

# اینجا میتونیم ربات رو با یه لیست از مکالمات آموزش بدیم
trainer_list = ListTrainer(chatbot)

# چند تا نمونه مکالمه
trainer_list.train([
    "سلام",
    "سلام، چطور میتونم کمکت کنم؟",
    "حالت چطوره؟",
    "من خوبم، ممنون. تو چطوری؟",
    "منم خوبم",
    "خوبه!",
    "اسم تو چیه؟",
    "من هوشنگ بات هستم.",
    "خداحافظ",
    "خداحافظ! روز خوبی داشته باشی."
])

# میتونیم از دیتاست‌های آماده هم استفاده کنیم (برای زبان فارسی)
# این دیتاست‌ها شامل مکالمات عمومی هستن
trainer_corpus = ChatterBotCorpusTrainer(chatbot)
trainer_corpus.train('chatterbot.corpus.persian') # برای زبان فارسی

print("ربات آماده است! شروع به صحبت کن (برای خروج بنویس 'خداحافظ'):")

# حلقه اصلی مکالمه
while True:
    try:
        user_input = input("شما: ")
        if user_input.lower() == 'خداحافظ':
            print("HooshangBot: خداحافظ! روز خوبی داشته باشی.")
            break

        bot_response = chatbot.get_response(user_input)
        print(f"HooshangBot: {bot_response}")

    except(KeyboardInterrupt, EOFError, SystemExit):
        break
    