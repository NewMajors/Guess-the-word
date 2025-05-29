from telegram.ext import Application, MessageHandler, filters, CommandHandler, ConversationHandler
from telegram import ReplyKeyboardMarkup
from config import Token_for_Bot


statistics = {'name' : 'None', 'country' : 'None', 'town' : 'None', 'count' : 0}
reply_keyboard = [["/login", "/help", "/profile"], ["/play"]]

markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
markup2 = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)


async def start(update, context):
    await update.message.reply_text(f'Добро пожаловать {update.message.from_user.first_name}! \
        Зарегестрируйтесь, использовав команду: /login', reply_markup=markup2)


async def login(update, context):
    if statistics['name'] == 'None' and statistics['country'] == 'None' and statistics['town'] == 'None':
        await update.message.reply_text('Введите свой никнейм: ')
        return 1
    else:
        await update.message.reply_text('Вы уже зарегестрированы')
    
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
    else:
        await update.message.reply_text(f'''Ваши никнейм:  _{statistics['name']}_ 
Страна:  _{statistics['country']}_
Город:  _{statistics['town']}_''')
        

async def help(update, context):
    await update.message.reply_text(f'''/login - команда, для регистрации
/profile - команда, чтобы увидеть данные вашего профиля
/play - команда, для запуска игры     
/start - команда, для запуска бота
''')


async def play(update, context):
    if "None" in statistics.values():
        await update.message.reply_text('Закончите регистрацию: ')
    else:
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
    
    help_handler = CommandHandler('help', help)
    start_handler = CommandHandler('start', start)
    play_handler = CommandHandler('play', play)
    profile_handler = CommandHandler('profile', profile)
    text_handler = MessageHandler(filters.TEXT, func)
    
    aplication.add_handler(start_handler)
    aplication.add_handler(conv_handler)
    aplication.add_handler(help_handler)
    aplication.add_handler(play_handler)
    aplication.add_handler(profile_handler)
    aplication.add_handler(text_handler)
    
    aplication.run_polling()
    
    
if __name__ == "__main__":
    main()