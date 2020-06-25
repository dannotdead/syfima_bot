import telebot
import re
import subprocess
import threading
from vk_integration import activate_vk_bot
from telebot import types
from tokens import token_telegram

def activate_telegram_bot():
    bot = telebot.TeleBot(token_telegram)

    flag_vk = 0 # если пользователь хочет отправить сообщение в VK
    flag_mail = 0 # если пользователь хочет отправить сообщение на почту
    # нужны для состояния данных от пользователя такие как id или mail

    # мб просто переменные, пока хранится в массиве для нескольких vkid и mail
    # vk_id = [] # хранит в себе id vk
    mail_id = [] # хранит в себе mail
    # старый вариант
    vk_id = ''
    # mail_id = ''

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
                    types.KeyboardButton('Telegram'), 
                    types.KeyboardButton('Почта')]
        markup = types.ReplyKeyboardMarkup(row_width=list_key.__len__(), resize_keyboard=True)
        markup.add(list_key[0], list_key[1], list_key[2])
        bot.send_message(message.from_user.id, "Куда Вы хотите чтобы я Вам ответил:", reply_markup=markup)
        
    @bot.message_handler(commands=['id']) # неизвестно насчет аргументов хэндлера, пока заглушка в виде команды
    def get_vk_id(message):
        nonlocal vk_id, flag_vk
        pattern = re.compile(r'\d')
        result = pattern.findall(message.text)
        if result:
            vk_id = message.text
            flag_vk = 0
            bot.send_message(message.from_user.id, 'Сообщение отправлено')
            print('работает')
        else:
            bot.send_message(message.from_user.id, 'Введите id в виде числа')

    @bot.message_handler(commands=['mail']) # неизвестно насчет аргументов хэндлера, пока заглушка в виде команды
    def get_mail_id(message):
        nonlocal mail_id, flag_mail
        pattern = re.compile(r'[\w.-]+@[\w.-]+\.?[\w]+?')
        result = pattern.findall(message.text)
        if result:
            mail_id.append(message.text) # добавил почту в массив почт
            print(mail_id) # заглушка для БД
            flag_mail = 0
        else:
            bot.send_message(message.from_user.id, 'Введен неправильный адрес, попробуйте еще раз')

    @bot.message_handler(content_types=['text'])
    def get_text_messages(message):
        user_id = message.from_user.id
        # list_welcome = ['прив', 'привет', 'здравствуй', 'здарова', 'здаров', 'ку', 'хай', 'вассап', 'hi', 'hello']
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
            nonlocal flag_vk, vk_id
            flag_vk = 1
            if vk_id == '':
                bot.send_message(message.from_user.id, 'Напишите здесь id своей страницы в VK')
            else:
                bot.send_message(message.from_user.id, 'Мне уже известно ваше id в VK, отправляю сообщение') # заглушка для проверки
        elif message.text == 'Почта':
            nonlocal flag_mail
            flag_mail = 1
            if mail_id == []:
                bot.send_message(message.from_user.id, 'Напишите здесь свою почту')
            else:
                flag_mail = 0
                bot.send_message(message.from_user.id, 'Мне уже известна ваша почта, отправляю сообщение') # заглушка для проверки
        else:
            if flag_vk == 1:
                get_vk_id(message)
            elif flag_mail == 1:
                get_mail_id(message)
            else:
                bot.send_message(user_id, 'Я тебя не понимаю, давай общаться на человеческом языке, можешь, например, вызвать /help')

    bot.polling(none_stop=True, interval=2)

thread1 = threading.Thread(target=activate_telegram_bot, args=(), name='Active Telegram')
thread2 = threading.Thread(target=activate_vk_bot, args=(), name='Active VK')
thread1.start()
thread2.start()
