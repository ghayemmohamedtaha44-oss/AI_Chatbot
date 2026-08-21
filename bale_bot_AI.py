import asyncio
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, AIMessage
from bale import Bot, Message, Chat, User
from bale import Message

# ===== Ollama Settings =====
BASE_URL = "http://office.sadidafarin.ir:11434"
MODEL_NAME = "llama3.2:latest"

# Create LangChain client
model = ChatOllama(
    model=MODEL_NAME,
    base_url=BASE_URL,
    temperature=0.7,
)

# ===== Bale Bot Settings =====
TOKEN = "1097661845:chidj5aZzJc_lVXb4Q-zruMVQyYvbAAAHH4"  # Replace with your actual token
client = Bot(token=TOKEN)

# Dictionary to store conversation history per user
user_histories = {}

def get_ai_response(user_id: int, user_message: str) -> str:
    """Get response from AI model while preserving user history"""
    
    # Get or create history for user
    if user_id not in user_histories:
        user_histories[user_id] = []

    history = user_histories[user_id]
    
    # Add user's new message to history
    history.append({"role": "user", "content": user_message})

    # Convert history to LangChain format
    lc_messages = []
    for msg in history:
        if msg["role"] == "user":
            lc_messages.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            lc_messages.append(AIMessage(content=msg["content"]))

    # Get response from model
    full_response = ""
    try:
        for chunk in model.stream(lc_messages):
            if chunk.content:
                full_response += chunk.content
    except Exception as e:
        full_response = f"❌ Error connecting to AI model: {str(e)}"

    # Add bot's response to history
    if full_response:
        history.append({"role": "assistant", "content": full_response})
    else:
        full_response = "❌ No response received."
        history.append({"role": "assistant", "content": full_response})
        
    return full_response

# ===== Bot Commands and Handlers =====

@client.listen('on_ready')
async def on_ready_handler():
    """When bot is ready, print message in terminal."""
    print(f"{client.user} is ready!")

#@client.handle(Command("start"))
#async def start_command(message: Message):
    #"""Response to /start command"""
    #await message.reply("Hello! I am an AI chatbot. Ask me anything!")

@client.handle(Message())
async def echo_all(message: Message):
    """Main handler to receive and process all text messages"""
    
    # Check if message is text
    if not isinstance(message, Message) or not message.text:
        return
        
    # Get message text and user ID
    user_message = message.text
    user_id = message.author.id
    
    # Notify user that processing is happening
    await message.reply("🤔 Thinking...")
    
    # Get response from AI
    response = get_ai_response(user_id, user_message)
    
    # Send response to user
    await message.reply(response)

# ===== Run Bot =====
if __name__ == "__main__":
    print("Bot is running...")
    client.run