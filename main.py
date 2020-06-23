import telebot
from telebot import types

bot = telebot.TeleBot('1213620038:AAHIMjiAN56iioRKPzYINk5N7CcICJer46g')

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.from_user.id, 'Давай начнем, /help для вызова команд')

@bot.message_handler(commands=['help'])
def send_help(message):
    list_help = '1. /start - начало работы \n2. /help - помощь по командам \n3. /choose_loc - выбор где вы хотите продолжить общение'
    bot.send_message(message.from_user.id, list_help)
    list_key = [types.KeyboardButton('1'),
                types.KeyboardButton('2'),
                types.KeyboardButton('3')]
    markup = types.ReplyKeyboardMarkup(row_width=list_key.__len__(), resize_keyboard=True)
    markup.add(list_key[0], list_key[1], list_key[2])
    bot.send_message(message.from_user.id, 'Выберите команду:', reply_markup=markup)

@bot.message_handler(commands=['choose_loc'])
def send_loc(message):
    list_key = [types.KeyboardButton('VK'),
                types.KeyboardButton('Telegram')]
    markup = types.ReplyKeyboardMarkup(row_width=list_key.__len__(), resize_keyboard=True)
    markup.add(list_key[0], list_key[1])
    bot.send_message(message.from_user.id, "Выберите куда отправить ответ:", reply_markup=markup)
    

@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    user_id = message.from_user.id
    global flag
    list_welcome = ['прив', 'привет', 'здравствуй', 'здарова', 'здаров', 'ку', 'хай', 'вассап', 'hi', 'hello']
    # listSearch = ['', '', '', '', '']
    # if message.text.lower() in list_welcome:
    #     print(user_id)
    #     bot.send_message(user_id, 'Привет, чем я могу тебе помочь? \nПиши /help для получения всех комманд')
    if message.text == '1':
        send_welcome(message)
    elif message.text == '2':
        send_help(message)
    elif message.text == '3':
       send_loc(message)
    elif message.text == 'VK':
        print(user_id)
        bot.send_message(user_id, 'Напиши здесь id своей страницы в VK')
        flag = 'true'
    elif flag == 'true':
        vk_id = 'https://vk.com/' + message.text
        flag = 'false'
        print(vk_id)
    else:
        print(user_id, flag)
        bot.send_message(user_id, 'Я тебя не понимаю, давай общаться на человеческом языке, можешь, например, поздороваться')

bot.polling(none_stop=True, interval=5)