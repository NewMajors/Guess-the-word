from telegram.ext import Application, MessageHandler, filters, CommandHandler, ConversationHandler
from telegram import ReplyKeyboardMarkup
from config import Token_for_Bot


statistics = {'name' : 'None', 'country' : 'None', 'town' : 'None', 'count' : 0}
reply_keyboard = [["/login", "/play", "/profile"], ["/help", "/quit"]]

markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
markup2 = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)


async def start(update, context):
    await update.message.reply_text(f'Добро пожаловать {update.message.from_user.first_name}! \
        Зарегестрируйтесь, использовав команду: /login', reply_markup=markup2)


async def login(update, context):
    await update.message.reply_text('Введите свой никнейм: ')
    return 1
    
    
async def first_answer(update, context):
    statistics['name'] = update.message.text
    await update.message.reply_text('В какой стране вы проживаете: ')
    return 2


async def second_answer(update, context):
    statistics['country'] = update.message.text 
    await update.message.reply_text('В каком городе вы проживаете: ')
    return 3


async def three_answer(update, context):
    statistics['town'] = update.message.text 
    await update.message.reply_text('Данные сохранены!')
    return ConversationHandler.END


async def profile(update, context):
    if "None" in statistics.values():
        await update.message.reply_text('Закончите регистрацию: ')
        
    
async def menu(update, context):
    await update.message.reply_text(reply_markup=markup)
        

async def remove_menu(update, context):
    await update.message.reply_text('Меню убрано', reply_markup=markup2)


async def play(update, context):
    await update.message.reply_text('Начинаем игру')
    

async def leave(update, context):
    return ConversationHandler.END


async def func(update, context):
    await update.message.reply_text(update.message.text)
    

def main():
    aplication = Application.builder().token(Token_for_Bot).build()
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('login', login)],
        states={
            1: [MessageHandler(filters.TEXT & ~filters.COMMAND, first_answer)],
            2: [MessageHandler(filters.TEXT & ~filters.COMMAND, second_answer)], 
            3: [MessageHandler(filters.TEXT & ~filters.COMMAND, three_answer)]
        },
        fallbacks=[CommandHandler("stop", leave)]
    )
    
    start_handler = CommandHandler('start', start)
    play_handler = CommandHandler('play', play)
    remove_menu_handler = CommandHandler('hidemenu', remove_menu)
    profile_handler = CommandHandler('profile', profile)
    menu_handler = CommandHandler('menu', menu)
    text_handler = MessageHandler(filters.TEXT, func)
    
    aplication.add_handler(start_handler)
    aplication.add_handler(conv_handler)
    aplication.add_handler(play_handler)
    aplication.add_handler(remove_menu_handler)
    aplication.add_handler(profile_handler)
    aplication.add_handler(menu_handler)
    aplication.add_handler(text_handler)
    
    aplication.run_polling()
    
    
if __name__ == "__main__":
    main()