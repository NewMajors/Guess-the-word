from telegram.ext import Application, MessageHandler, filters
from config import Token_for_Bot

async def func(update, context):
    print(update.message.chat.first_name)


def main():
    aplication = Application.builder().token(Token_for_Bot).build()
    text_handler = MessageHandler(filters.TEXT, func)
    
    aplication.add_handler(text_handler)
    
    aplication.run_polling()
    
    
if __name__ == "__main__":
    main()