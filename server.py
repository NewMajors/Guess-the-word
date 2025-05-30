from telegram.ext import Application, MessageHandler, filters, CommandHandler, ConversationHandler
from telegram import ReplyKeyboardMarkup
from config import Token_for_Bot, url_translate_to_russian, url_get_translated_word

import sqlite3
import requests
import re

CHOOSE, GUESS_WORD, NUMERIC_INPUT_MODE = range(3)

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

statistics = {'id': 0, 'name': 'None', 'country': 'None', 'town': 'None', 'count': 0}
reply_keyboard = [["/login", "/help", "/profile"], ["/play"], ['/deleteProfile']]

markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
markup2 = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)


async def translate_to_russian(word):
    url = url_translate_to_russian
    params = {"q": word, "langpair": "en|ru"}
    
    try:
        response = requests.get(url, params=params, timeout=5)
        
        if response.status_code == 200:
            return response.json()["responseData"]["translatedText"]
        return "(ошибка API)"
    
    except requests.exceptions.RequestException:
        return "(ошибка подключения)"

async def get_translated_word():
    url = url_get_translated_word
    
    while True:
        try:
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                word = response.json()[0]
                translated = await translate_to_russian(word)
                
                if translated:
                    translated = translated.strip()
                    
                    if (" " not in translated and len(translated) <= 15 and 
                        re.fullmatch(r"[А-Яа-яЁё\-]+", translated)):
                        return word, translated
            return None, None
        except requests.exceptions.RequestException:
            return None, None


async def start(update, context):
    if "None" in statistics.values():
        await update.message.reply_text(
            f'Добро пожаловать {update.message.from_user.first_name}! Зарегистрируйтесь командой: /login',
            reply_markup=markup2
        )
    else:
        await update.message.reply_text('<!! ПРИВЕТСТВУЮ !!>')


async def login(update, context):
    statistics['id'] = update.message.from_user.id
    
    if "None" in statistics.values():
        await update.message.reply_text('Введите свой никнейм: ')
        return 1
    else:
        await update.message.reply_text('Вы уже зарегистрированы!')


async def first_answer(update, context):
    statistics['name'] = update.message.text
    await update.message.reply_text('В какой стране вы проживаете:')
    return 2


async def second_answer(update, context):
    statistics['country'] = update.message.text
    await update.message.reply_text('В каком городе вы проживаете:')
    return 3


async def three_answer(update, context):
    statistics['town'] = update.message.text
    statistics['count'] = 0

    cursor.execute('''
    INSERT OR REPLACE INTO users (id, name, country, town, count) 
    VALUES (?, ?, ?, ?, ?)''', (
        statistics['id'], statistics['name'],
        statistics['country'], statistics['town'], statistics['count']
    ))
    connection.commit()
    await update.message.reply_text('Данные сохранены!')
    return ConversationHandler.END


async def profile(update, context):
    if "None" in statistics.values():
        await update.message.reply_text('Сначала зарегистрируйтесь.')
        return
    
    cursor.execute('SELECT name, country, town, count FROM users WHERE id = ?', (statistics['id'],))
    result = cursor.fetchone()
    
    if result:
        name, country, town, count = result
        await update.message.reply_text(
            f'''Ваш профиль:
Никнейм: _{name}_
Страна: _{country}_
Город: _{town}_
Слов угадано: _{count}_''')
    else:
        await update.message.reply_text('Профиль не найден.')


async def delete_profile(update, context):
    if 'None' in statistics.values():
        await update.message.reply_text('Сначала зарегистрируйтесь.')
    else:
        cursor.execute('DELETE FROM users WHERE id = ?', (statistics['id'],))
        connection.commit()
        statistics.update({'id': 0, 'name': 'None', 'country': 'None', 'town': 'None', 'count': 0})
        await update.message.reply_text('Профиль удалён. Введите никнейм для повторной регистрации:')
        return 1


async def help(update, context):
    await update.message.reply_text('''Доступные команды:
/login — регистрация
/profile — ваш профиль
/play — сыграть в "угадай слово"
/start — запуск бота
/deleteProfile — удалить профиль
''')


async def play(update, context):
    if "None" in statistics.values():
        await update.message.reply_text('Сначала зарегистрируйтесь через /login.')
        return ConversationHandler.END

    eng, rus = await get_translated_word()
    
    if eng and rus:
        context.user_data['answer'] = rus
        await update.message.reply_text(
            f"В этом слове {len(rus)} букв. Ты можешь выбрать 1 из 2 действий:\n"
            "1 - Ввести слово целиком\n"
            "2 - Ввести букву\n"
            "Если выберишь 1, то у тебя одна попытка, чтобы разгадать слово.\n"
            "Если выберишь 2, то у тебя 6 попыток, после чего тебе придется разгадывать слово"
        )
        return CHOOSE
    else:
        await update.message.reply_text("Ошибка при получении слова.")
        return ConversationHandler.END


async def choose_mode(update, context):
    choice = update.message.text.strip()
    
    if choice == '1':
        await update.message.reply_text('Введите предполагаемое слово:')
        return GUESS_WORD
    elif choice == '2':
        await update.message.reply_text('Введите букву: ')
        return NUMERIC_INPUT_MODE
    else:
        await update.message.reply_text('Введите только 1 или 2.')
        return CHOOSE


async def guess_word(update, context):
    guess = update.message.text.strip().lower()
    correct = context.user_data.get('answer', '').lower()

    if guess == correct:
        await update.message.reply_text('Поздравляю! Вы угадали слово.')
        statistics['count'] += 1
        cursor.execute('UPDATE users SET count = ? WHERE id = ?', (statistics['count'], statistics['id']))
        connection.commit()
    else:
        await update.message.reply_text(f'Неверно. Загаданное слово было: {correct}')
    return ConversationHandler.END


async def numeric_input_mode(update, context):
    letter = update.message.text.strip().lower()
    correct = context.user_data.get('answer', '').lower()
    
    guessed_letters = context.user_data.setdefault('guessed_letters', [])
    attempts_left = context.user_data.setdefault('attempts_left', 6)

    if len(letter) != 1 or not letter.isalpha():
        await update.message.reply_text("Введите только одну букву.")
        return NUMERIC_INPUT_MODE

    if letter in guessed_letters:
        await update.message.reply_text("Вы уже называли эту букву.")
        return NUMERIC_INPUT_MODE

    guessed_letters.append(letter)

    if letter in correct:
        context.user_data['attempts_left'] -= 1
        await update.message.reply_text(
            f"Такая буква есть в слове. Осталось попыток: {context.user_data['attempts_left']}"
        )
    else:
        context.user_data['attempts_left'] -= 1
        await update.message.reply_text(
            f"Такой буквы нет. Осталось попыток: {context.user_data['attempts_left']}"
        )

    display = " ".join([c if c in guessed_letters else "_" for c in correct])
    await update.message.reply_text(f"Слово: {display}")

    if all(c in guessed_letters for c in correct):
        await update.message.reply_text(f"Поздравляю! Вы угадали слово: {correct}")
        statistics['count'] += 1
        cursor.execute('UPDATE users SET count = ? WHERE id = ?', (statistics['count'], statistics['id']))
        connection.commit()
        return ConversationHandler.END

    if context.user_data['attempts_left'] <= 0:
        await update.message.reply_text("Попытки закончились. Теперь попробуй угадать слово целиком:")
        return GUESS_WORD

    return NUMERIC_INPUT_MODE


async def leave(update, context):
    return ConversationHandler.END


def main():
    application = Application.builder().token(Token_for_Bot).build()

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
            3: [MessageHandler(filters.TEXT & ~filters.COMMAND, three_answer)]
        },
        fallbacks=[CommandHandler("stop", leave)]
    )

    game_handler = ConversationHandler(
        entry_points=[CommandHandler('play', play)],
        states={
            CHOOSE: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_mode)],
            GUESS_WORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, guess_word)],
            NUMERIC_INPUT_MODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, numeric_input_mode)]
        },
        fallbacks=[CommandHandler("stop", leave)]
    )

    application.add_handler(CommandHandler('start', start))
    application.add_handler(conv_handler)
    application.add_handler(delete_profile_handler)
    application.add_handler(game_handler)
    application.add_handler(CommandHandler('help', help))
    application.add_handler(CommandHandler('profile', profile))

    application.run_polling()
    connection.close()

if __name__ == "__main__":
    main()