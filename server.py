from telegram.ext import Application, MessageHandler, filters, CommandHandler
from telegram import ReplyKeyboardMarkup
from config import Token_for_Bot


statistics = {'name' : 'None', 'country' : 'None', 'town' : 'None', 'count' : 0}
user_state = {}

reply_keyboard = [["/start", "/login", "/play"], ["/help", "/quit"]]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
markup2 = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)


async def start(update, context):
    await update.message.reply_text(f'Добро пожаловать {update.message.from_user.first_name}! \
        Зарегестрируйтесь, использовав команду: /login', reply_markup=markup)
    

async def login(update, context):
    user_id = update.message.from_user.id
    user_state[user_id] = 'awaiting_name' 
    await update.message.reply_text('Введите свой никнейм:')


async def remove_menu(update, context):
    await update.message.reply_text('Меню убрано', reply_markup=markup2)


async def play(update, context):
    await update.message.reply_text('Начинаем игру')
    

async def leave(update, context):
    pass


async def func(update, context):
    user_id = update.message.from_user.id
    text = update.message.text

    state = user_state.get(user_id)

    if state == 'awaiting_name':
        statistics['name'] = text
        user_state[user_id] = 'awaiting_country'
        await update.message.reply_text('В какой стране вы проживаете:')
        return

    if state == 'awaiting_country':
        statistics['country'] = text
        user_state[user_id] = 'awaiting_town'
        await update.message.reply_text('В каком городе вы проживаете:')
        return

    if state == 'awaiting_town':
        statistics['town'] = text
        user_state.pop(user_id)  # регистрация завершена
        await update.message.reply_text('Данные сохранены')
        return
    

def main():
    aplication = Application.builder().token(Token_for_Bot).build()
    text_handler = MessageHandler(filters.TEXT, func)
    start_handler = CommandHandler('start', start)
    login_handler = CommandHandler('login', login)
    play_handler = CommandHandler('play', play)
    leave_handler = CommandHandler('leave', leave)
    remove_menu_handler = CommandHandler('hidemenu', remove_menu)
    
    aplication.add_handler(start_handler)
    aplication.add_handler(leave_handler)
    aplication.add_handler(play_handler)
    aplication.add_handler(login_handler)
    aplication.add_handler(remove_menu_handler)
    aplication.add_handler(text_handler)
    
    aplication.run_polling()
    
    
if __name__ == "__main__":
    main()