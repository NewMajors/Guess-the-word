from telegram.ext import Application, MessageHandler, filters, CommandHandler, ConversationHandler
from telegram import ReplyKeyboardMarkup
from config import Token_for_Bot

import sqlite3

connection = sqlite3.connect('DB/DataBase.sqlite')

cursor = connection.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    country TEXT NOT NULL,
    town TEXT NOT NULL, 
    count INTEGER NOT NULL)
''')

cursor.execute('''SELECT * FROM users''')

statistics = {'id': 0, 'name': 'None', 'country': 'None', 'town': 'None', 'count': 0}
reply_keyboard = [["/login", "/help", "/profile"], ["/play"], ['/deleteProfile']]

markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
markup2 = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)


async def start(update, context):
    await update.message.reply_text(f'Добро пожаловать {update.message.from_user.first_name}! \
        Зарегестрируйтесь, использовав команду: /login', reply_markup=markup2)


async def login(update, context):
    statistics['id'] = update.message.from_user.id 
    
    if "None" in statistics.values():
        await update.message.reply_text('Введите свой никнейм: ')
        return 1
    else:
        await update.message.reply_text('Вы уже зарегестрированы!')
    

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
    statistics['count'] = 0
    
    cursor.execute('''
INSERT INTO users (id, name, country, town, count) 
VALUES (?, ?, ?, ?, ?)
''', (statistics['id'], statistics['name'], statistics['country'], statistics['town'], statistics['count']))
    
    connection.commit()
    
    await update.message.reply_text('Данные сохранены!')
    
    return ConversationHandler.END


async def profile(update, context):
    if "None" in statistics.values():
        await update.message.reply_text('Зарегестрируйтесь!!!')
        return

    cursor.execute('SELECT name, country, town, count FROM users WHERE id = ?', (statistics['id'],))
    result = cursor.fetchone()

    if result:
        name, country, town, count = result
        await update.message.reply_text(f'''Ваш профиль:
Никнейм: _{name}_
Страна: _{country}_
Город: _{town}_
Слов угадано: _{count}_''')
    else:
        await update.message.reply_text('Профиль не найден. Зарегистрируйтесь снова.')


async def delete_profile(update, context):
    if 'None' in statistics.values():
        await update.message.reply_text('Для начала зарегестрируйтесь!')
    else:
        cursor.execute('DELETE FROM users WHERE id = ?', (statistics['id'],))
        connection.commit()
        
        statistics['id'] = 0
        statistics['name'] = 'None'
        statistics['country'] = 'None'
        statistics['town'] = 'None'
        statistics['count'] = 0
        
        await update.message.reply_text('Ваш профиль был удалён. Зарегестрируйтесь заново.\nВведите свой никнейм:')
        return 1
    

async def help(update, context):
    await update.message.reply_text(f'''/login - команда, для регистрации
/profile - команда, чтобы увидеть данные вашего профиля
/play - команда, для запуска игры     
/start - команда, для запуска бота
/deleteProfile - команда, для удаления данных о профиле
''')


async def play(update, context):
    if "None" in statistics.values():
        await update.message.reply_text('Зарегестрируйтесь!!!')
    else:
        await update.message.reply_text('Начинаем игру')
    

async def leave(update, context):
    return ConversationHandler.END


async def func(update, context):
    pass
    

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
    
    delete_profile_handler = ConversationHandler(
        entry_points=[CommandHandler('deleteProfile', delete_profile)],
        states={
            1: [MessageHandler(filters.TEXT & ~filters.COMMAND, first_answer)],
            2: [MessageHandler(filters.TEXT & ~filters.COMMAND, second_answer)],
            3: [MessageHandler(filters.TEXT & ~filters.COMMAND, three_answer)],
        },
        fallbacks=[CommandHandler("stop", leave)]
    )
    
    help_handler = CommandHandler('help', help)
    start_handler = CommandHandler('start', start)
    play_handler = CommandHandler('play', play)
    profile_handler = CommandHandler('profile', profile)
    login_handler = CommandHandler('login', login)
    text_handler = MessageHandler(filters.TEXT, func)
    
    aplication.add_handler(start_handler)
    aplication.add_handler(conv_handler)
    aplication.add_handler(help_handler)
    aplication.add_handler(play_handler)
    aplication.add_handler(profile_handler)
    aplication.add_handler(login_handler)
    aplication.add_handler(delete_profile_handler)
    aplication.add_handler(text_handler)
    
    aplication.run_polling()
    connection.close()
    
    
if __name__ == "__main__":
    main()