from telegram.ext import Application, MessageHandler, filters, CommandHandler
from telegram import ReplyKeyboardMarkup
from config import Token_for_Bot

reply_keyboard = [["/help", "/start"], ["/login", "/quit"]]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
markup2 = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

async def leave(update, context):
    pass

async def play(update, context):
    pass

async def login(update, context):
    pass


async def start(update, context):
    await update.message.reply_text(f'Добро пожаловать {update.message.from_user.first_name}!', reply_markup=markup)

async def func(update, context):
    print(update.message.text)
    await update.message.reply_text(update.message.text)

def main():
    aplication = Application.builder().token(Token_for_Bot).build()
    text_handler = MessageHandler(filters.TEXT, func)
    start_handler = CommandHandler('start', start)
    leave_handler = CommandHandler('leave', leave)
    play_handler = CommandHandler('play', play)
    login_handler = CommandHandler('login', login)
    
    aplication.add_handler(start_handler)
    aplication.add_handler(text_handler)
    aplication.add_handler(leave_handler)
    aplication.add_handler(play_handler)
    aplication.add_handler(login_handler)
    
    aplication.run_polling()
    
    
if __name__ == "__main__":
    main()