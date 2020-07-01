import telebot
import re
import tokens
import server

def activate_telegram_bot():
    bot = telebot.TeleBot(tokens.token_telegram)

    # отказываться от простых флагов и менять флаги для определенного пользователя 

    # хранится порядковый номер пользователя
    # если сервер перезапущен то берется из БД и прибавляется 1 для новых пользователей
    result = server.get_serial_number_after_restart()
    new_user_ser_num = int(result[0]) + 1 

    flag_vk = 0 # если пользователь хочет отправить сообщение в VK
    flag_mail = 0 # если пользователь хочет отправить сообщение на почту
    flag_reg = 0
    flag_reg_vk = 0
    # нужны для состояния данных от пользователя такие как id или mail
    flag_question = 0
    # мб просто переменные, пока хранится в массиве для нескольких vkid и mail
    vk_id = 0 # хранит в себе id vk
    mail_id = [] # хранит в себе mail
    # старый вариант
    # mail_id = ''
    # new_user_key = 1
    
    # user_data = {}

    def generate_keyboard(*answer): 
        # Метод который создает клавиатуру с кнопками   
        keyboard = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        for item in answer:
            button = telebot.types.KeyboardButton(item)
            keyboard.add(button)
        return keyboard

    @bot.message_handler(commands=['start'])
    def send_welcome(message):
        nonlocal new_user_ser_num
        check_reg_telegram = server.new_account_telegram(new_user_ser_num, message.chat.id)
        # если проверка прошла успешно и пользователь не найден в БД
        # то я увеличиваю пару ключ значение на 1
        if check_reg_telegram:
            result = server.get_serial_number_after_restart()
            new_user_ser_num = int(result[0]) + 1
        bot.send_message(message.from_user.id, 'Давайте начнем, /help для вызова команд')

    @bot.message_handler(commands=['help'])
    def send_help(message):
        keyboard = generate_keyboard('/start', '/help', '/choose_loc', '/question', '/my_id')
        bot.send_message(message.from_user.id,   '1. /start - начало работы \
                                                \n2. /help - помощь по командам \
                                                \n3. /choose_loc - выбор где вы хотите продолжить общение \
                                                \n4. /question - задайте мне вопрос \
                                                \n5. /my_id - узнать свой id для авторизации через другие мессенджеры \
                                                \nВыберите команду:', reply_markup=keyboard)

    @bot.message_handler(commands=['choose_loc'])
    def send_loc(message):
        keyboard = generate_keyboard('VK', 'Telegram', 'Почта')
        bot.send_message(message.from_user.id, 'Куда вы хотите чтобы я вам ответил:', reply_markup=keyboard)
        
    @bot.message_handler(commands=['question'])
    def get_question(message):
        nonlocal flag_question
        flag_question = 1
        list_help = '1. Компьютерные технологии \n2. Менеджмент \n3. Игры \n4. Математика'
        bot.send_message(message.from_user.id, list_help)
        bot.send_message(message.from_user.id, 'Задайте мне вопрос на одну из тем')
            
    @bot.message_handler(commands=['my_id'])
    def get_my_id(message):
        # нужен для авторизации в других мессенджерах, чтобы другие мессенджеры поняли в какую строку в БД записывать свои id
        # метод который позволяет вывести id пользователя
        # данные беруться из БД
        # проверка id telegram пользователя и возврат его id
        my_id = server.get_my_id_from_db(message.chat.id, 1)
        bot.send_message(message.chat.id, 'Ваш уникальный идентификатор пользователя: ' + str(my_id))

    def send_question(message):
        # метод который ищет вопрос в БД
        nonlocal flag_question
        flag_question = 0
        ret = server.call_db(message)

    def get_mail_id(message):
        nonlocal mail_id, flag_mail
        pattern = re.compile(r'[\w.-]+@[\w.-]+\.?[\w]+?')
        result = pattern.findall(message.text)
        # если пришло true значит спрашиваем отправить письмо на эту почту?: (почта)
            # если пользователь ответит ДА, то отправляем ему письмо на данную почту: (почта)
            # если пользователь ответи НЕТ, то просим ввести эл адрес и затем отправляем
        # если пришло false значит просим ввести эл адрес и затем отправляем
        # далее выводим, что сообщение отправлено

        #НЕ ДОДЕЛАНА ПРОВЕРКА ПОЧТЫ ДО КОНЦА
        
        if result:
            flag_mail = 0
            send_text = server.send_mail(message.text)
            if send_text:
                bot.send_message(message.from_user.id, 'Сообщение отправлено, проверьте письмо во вкладке входящих сообщений или спама')
            else: 
                bot.send_message(message.from_user.id, 'Что-то пошло не так')
        else:
            bot.send_message(message.from_user.id, 'Введен неправильный адрес, попробуйте еще раз')

    @bot.message_handler(content_types=['text'])
    def get_text_messages(message):
        user_id = message.from_user.id
        nonlocal flag_reg, flag_reg_vk, flag_question, flag_mail

        if message.text.lower() == 'vk':
            msg = server.check_vk_db(message.chat.id, 1) # проверка зарегестрирован ли пользователь в БД с VK-id
            if msg:            
                bot.send_message(user_id, 'Сообщение отправлено')
            else:
                bot.send_message(user_id, 'Напишите боту в VK свой id (команда /my_id), чтобы он мог вам туда ответить, а также разрешите отправлять сообщения и повторите попытку\n' + tokens.bot_vk_url)
        elif message.text.lower() == 'telegram':
            msg = server.call_db(message) # Обработка сообщения на сервере и ответ прямо в телегу
            bot.send_message(user_id, msg)
        elif message.text.lower() == 'почта':
            check_mail, mail = server.check_mail(message.chat.id, 1)
            if check_mail:
                bot.send_message(user_id, 'Возможно вы хотите отправить на эту почту: ' + mail + ' это так?')
            else:
                flag_mail = 1
                bot.send_message(user_id, 'Введите почту')
        else:
            # if flag_reg_vk == 1:
            #     get_vk_id(message)
            # el
            if flag_mail == 1:
                get_mail_id(message)
            elif flag_question == 1:
                send_question(message)
            else:
                bot.send_message(user_id, 'Я тебя не понимаю, давай общаться на человеческом языке, можешь, например, вызвать /start')

    bot.polling(none_stop=True, interval=2)