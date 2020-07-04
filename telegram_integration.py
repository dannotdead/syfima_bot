import telebot
import re
import tokens
import server
from enum import Enum

class States(Enum):
    # Состояния пользователя
    S_START = '1' 
    S_QUESTION = '2'
    S_CHOOSE_LOC = '3'
    S_CHOOSE_LOC_VK = '3.1'
    S_CHOOSE_LOC_MAIL = '3.2'
    S_FEEDBACK = '4' # Состояние обратная связь

def activate_telegram_bot():
    bot = telebot.TeleBot(tokens.token_telegram)

    def generate_keyboard(*answer): 
        # Метод который создает клавиатуру с кнопками   
        keyboard = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        for item in answer:
            button = telebot.types.KeyboardButton(item)
            keyboard.add(button)
        return keyboard

    @bot.message_handler(commands=['start'])
    def send_welcome(message):
        # начало
        bot.send_message(message.chat.id, 'Давайте начнем, задайте мне вопрос. Для вызова всех команд используйте /help')
        server.db_set_state(message.chat.id, 1, States.S_QUESTION.value)

    @bot.message_handler(func=lambda message: server.db_get_state(message.chat.id, 1) == States.S_QUESTION.value)
    def send_question(message):
        # проверка вопроса в БД
        detect = server.find_question(message.chat.id, 1, message.text)
        if detect:
            bot.send_message(message.chat.id, 'Ответ на заданный вопрос найден')
            keyboard = generate_keyboard('VK', 'Telegram', 'Почта')
            bot.send_message(message.chat.id, 'Куда вы хотите чтобы я вам ответил:', reply_markup=keyboard)
            server.db_set_state(message.chat.id, 1, States.S_CHOOSE_LOC.value)
        else:
            if message.text == '/help':
                send_help(message)
            else:
                bot.send_message(message.chat.id, 'Ответ не был найден, попробуйте задать вопрос снова')
    
    @bot.message_handler(func=lambda message: server.db_get_state(message.chat.id, 1) == States.S_CHOOSE_LOC.value)
    def send_answer(message):
        # выбор куда отправить сообщение
        if message.text.lower() == 'vk':
            check_vk_id = server.check_vk_db(message.chat.id, 1)
            if check_vk_id:
                bot.send_message(message.chat.id, 'Сообщение отправлено в VK')
                server.db_set_state(message.chat.id, 1, States.S_QUESTION.value) # Должно переходить в S_FEEDBACK
                bot.send_message(message.chat.id, 'Задайте мне вопрос')
            else:
                bot.send_message(message.chat.id, 'Я не знаю ваш VK-id напишите его, а также разрешите отправлять мне сообщения в VK в диалоге' + tokens.bot_vk_url)
                server.db_set_state(message.chat.id, 1, States.S_CHOOSE_LOC_VK.value)
        elif message.text.lower() == 'telegram':
            answer = server.send_answer_to_telegram(message.chat.id, 1)
            bot.send_message(message.chat.id, 'Ответ на заданный вопрос: ' + answer)
            server.db_set_state(message.chat.id, 1, States.S_QUESTION.value) # Должно переходить в S_FEEDBACK
            bot.send_message(message.chat.id, 'Задайте мне вопрос')
        elif message.text.lower() == 'почта':
            bot.send_message(message.chat.id, 'Пожалуйста напишите почту на которую хотите получить ответ')
            server.db_set_state(message.chat.id, 1, States.S_CHOOSE_LOC_MAIL.value)
    
    @bot.message_handler(func=lambda message: server.db_get_state(message.chat.id, 1) == States.S_CHOOSE_LOC_VK.value)
    def get_vk_id(message):
        # если хотим отправить сообщение в вк
        if not message.text.isdigit():
        # Состояние не меняем, поэтому только выводим сообщение об ошибке и ждём дальше
            bot.send_message(message.chat.id, 'VK-id - это 9-ти значное число, мне нужно число из 9 цифр')
            return
        if len(message.text) < 9 or len(message.text) > 9:
            bot.send_message(message.chat.id, 'Ровно 9 цифр пожалуйста')
            return
        else:
            vk_id_to_db = server.get_vk_db(message.text, message.chat.id)
            if vk_id_to_db:
                check_vk_id = server.check_vk_db(message.chat.id, 1)
                if check_vk_id:
                    bot.send_message(message.chat.id, 'Все верно, отправляю сообщение в VK')
                    server.db_set_state(message.chat.id, 1, States.S_QUESTION.value) # Должно переходить в S_FEEDBACK
                    bot.send_message(message.chat.id, 'Задайте мне вопрос')
                else:
                    bot.send_message(message.chat.id, 'Что-то пошло не так')
            else:
                bot.send_message(message.chat.id, 'Что-то пошло не так 2')

    @bot.message_handler(func=lambda message: server.db_get_state(message.chat.id, 1) == States.S_CHOOSE_LOC_MAIL.value)
    def get_mail(message):
        # если хотим отправить сообщение на почту
        pattern = re.compile(r'[\w.-]+@[\w.-]+\.?[\w]+?')
        result = pattern.findall(message.text)
        # если пришло true значит спрашиваем отправить письмо на эту почту?: (почта)
            # если пользователь ответит ДА, то отправляем ему письмо на данную почту: (почта)
            # если пользователь ответи НЕТ, то просим ввести эл адрес и затем отправляем
        # если пришло false значит просим ввести эл адрес и затем отправляем
        # далее выводим, что сообщение отправлено
        if result:
            send_text = server.send_mail(message.chat.id, 1, message.text)
            if send_text:
                bot.send_message(message.chat.id, 'Сообщение отправлено, проверьте письмо во вкладке входящих сообщений или спама')
                server.db_set_state(message.chat.id, 1, States.S_QUESTION.value) # Должно переходить в S_FEEDBACK
                bot.send_message(message.chat.id, 'Задайте мне вопрос')
            else: 
                bot.send_message(message.chat.id, 'Что-то пошло не так')
        else:
            bot.send_message(message.chat.id, 'Введен неправильный адрес, попробуйте еще раз')

    @bot.message_handler(commands=['help'])
    def send_help(message):
        # помощь
        keyboard = generate_keyboard('/start', '/help', '/choose_loc')
        bot.send_message(message.chat.id,   '1. /start - начало работы \
                                                \n2. /help - помощь по командам \
                                                \n3. /choose_loc - выбор где вы хотите продолжить общение \
                                                \nВыберите команду:', reply_markup=keyboard)

    @bot.message_handler(content_types=['text'])
    def get_text_messages(message):
        # если какойто посторонний текст то вывод данного сообщения
        bot.send_message(message.chat.id, 'Я тебя не понимаю, давай общаться на человеческом языке, можешь, например, вызвать /start')

    bot.polling(none_stop=True, interval=10)