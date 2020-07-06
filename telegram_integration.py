import re

import telebot

import tokens
import server
import user_states


def activate_telegram_bot():
    bot = telebot.TeleBot(tokens.token_telegram)

    # Функция которая создает клавиатуру с кнопками.
    def generate_keyboard(*answer):
        keyboard = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True,
                                                     resize_keyboard=True)
        for item in answer:
            button = telebot.types.KeyboardButton(item)
            keyboard.add(button)
        return keyboard

    # /reset для сброса состояния пользователя.
    @bot.message_handler(commands=['reset'])
    def reset_state(message):
        server.db_set_state(message.chat.id, 1, user_states.States.S_START.value)
        bot.send_message(message.chat.id, 'Вызовите команду /start')

    # Команда /start для начала диалога, есть проверка текущего состояния у пользователя.
    # В зависимости от состояния будет выводиться свое сообщение.
    @bot.message_handler(commands=['start'])
    def send_welcome(message):
        server.new_account_telegram(message.chat.id)
        state = server.db_get_state(message.chat.id, 1)
        if state == user_states.States.S_START.value:
            bot.send_message(message.chat.id, 'Задайте новый вопрос')
            server.db_set_state(message.chat.id, 1,
                                user_states.States.S_QUESTION.value)
        elif state == user_states.States.S_QUESTION.value:
            bot.send_message(message.chat.id,
                             'Можете задать мне вопрос')
        elif state == user_states.States.S_CHOOSE_LOC.value:
            bot.send_message(message.chat.id,
                             'Вы еще не выбрали куда вам отправить ответ')
        elif state == user_states.States.S_CHOOSE_LOC_VK.value:
            bot.send_message(message.chat.id,
                             'Вы еще не ввели VK-id')
        elif state == user_states.States.S_CHOOSE_LOC_MAIL.value:
            bot.send_message(message.chat.id,
                             'Вы еще не ввели свою почту')
        elif state == user_states.States.S_FEEDBACK.value:
            bot.send_message(message.chat.id,
                             'Вы еще не оставили отзыв об ответе')
        else:
            bot.send_message(message.chat.id,
                             'Давайте начнем, задайте мне вопрос. '
                             'Для вызова всех команд используйте /help')
            server.db_set_state(message.chat.id, 1,
                                user_states.States.S_QUESTION.value)

    # Описание команды /help.
    @bot.message_handler(commands=['help'])
    def send_help(message):
        keyboard = generate_keyboard('/start', '/help', '/choose_loc')
        bot.send_message(message.chat.id, '1. /start - начало работы \n'
                                          '2. /help - помощь по командам \n'
                                          '3. /choose_loc - выбор '
                                          'где вы хотите продолжить общение \n'
                                          'Выберите команду:',
                         reply_markup=keyboard)

    # Любой текст не связанный с запросами пользователя обрабатывается здесь.
    @bot.message_handler(content_types=['text'])
    def get_text_messages(message):
        bot.send_message(message.chat.id,
                         'Я тебя не понимаю, '
                         'давай общаться на человеческом языке, '
                         'можешь, например, вызвать /start')

    # Проверка наличия вопроса в базе данных,
    # если таковой имеется вывести поддерживаемые мессенджеры.
    @bot.message_handler(func=lambda message: server.db_get_state(message.chat.id, 1) == user_states.States.S_QUESTION.value)
    def send_question(message):
        detect = server.find_question(message.chat.id, 1, message.text)
        if detect:
            bot.send_message(message.chat.id, 'Ответ на заданный вопрос найден')
            keyboard = generate_keyboard('VK', 'Telegram', 'Почта')
            bot.send_message(message.chat.id,
                             'Куда вы хотите чтобы я вам ответил:',
                             reply_markup=keyboard)
            server.db_set_state(message.chat.id, 1,
                                user_states.States.S_CHOOSE_LOC.value)
        else:
            if message.text == '/help':
                send_help(message)
            else:
                bot.send_message(message.chat.id,
                                 'Ответ не был найден, попробуйте задать вопрос снова')

    # Выбор куда отправить ответ на вопрос.
    @bot.message_handler(func=lambda message: server.db_get_state(message.chat.id, 1) == user_states.States.S_CHOOSE_LOC.value)
    def send_answer(message):
        if message.text.lower() == 'vk':
            check_vk_id = server.check_vk_db(message.chat.id, 1)
            if check_vk_id:
                bot.send_message(message.chat.id, 'Сообщение отправлено в VK')
                bot.send_message(message.chat.id,
                                 'Надеюсь мне удалось вам помочь, '
                                 'оцените полученный ответ от 1 до 5')
                server.db_set_state(message.chat.id, 1,
                                    user_states.States.S_FEEDBACK.value)
            else:
                bot.send_message(message.chat.id,
                                 'Я не знаю ваш VK-id напишите его, '
                                 'а также разрешите отправлять ' 
                                 'мне сообщения в VK в диалоге ' + tokens.bot_vk_url)
                server.db_set_state(message.chat.id, 1,
                                    user_states.States.S_CHOOSE_LOC_VK.value)
        elif message.text.lower() == 'telegram':
            answer = server.send_answer_to_telegram(message.chat.id, 1)
            bot.send_message(message.chat.id, 'Ответ на заданный вопрос: ' + answer)
            bot.send_message(message.chat.id,
                             'Надеюсь мне удалось вам помочь, '
                             'оцените полученный ответ от 1 до 5')
            server.db_set_state(message.chat.id, 1,
                                user_states.States.S_FEEDBACK.value)
        elif message.text.lower() == 'почта':
            bot.send_message(message.chat.id,
                             'Пожалуйста напишите почту на которую хотите получить ответ')
            server.db_set_state(message.chat.id, 1,
                                user_states.States.S_CHOOSE_LOC_MAIL.value)

    # Блок кода для ввода VK-id, вызывается в том случае если пользователь хочет получить
    # ответ в VK, но его id нет в базе данных.
    # После получения верного id отправляем ответ.
    @bot.message_handler(func=lambda message: server.db_get_state(message.chat.id, 1) == user_states.States.S_CHOOSE_LOC_VK.value)
    def get_vk_id(message):
        if not message.text.isdigit():
            bot.send_message(message.chat.id,
                             'VK-id - это 9-ти значное число, мне нужно число из 9 цифр')
            return
        if len(message.text) < 9 or len(message.text) > 9:
            bot.send_message(message.chat.id, 'Ровно 9 цифр пожалуйста')
            return
        else:
            vk_id_to_db = server.get_vk_db(message.text, message.chat.id)
            if vk_id_to_db:
                check_vk_id = server.check_vk_db(message.chat.id, 1)
                if check_vk_id:
                    bot.send_message(message.chat.id,
                                     'Все верно, отправляю сообщение в VK')
                    bot.send_message(message.chat.id,
                                     'Надеюсь мне удалось вам помочь, '
                                     'оцените полученный ответ от 1 до 5')
                    server.db_set_state(message.chat.id, 1,
                                        user_states.States.S_FEEDBACK.value)
                else:
                    bot.send_message(message.chat.id, 'Что-то пошло не так')
            else:
                bot.send_message(message.chat.id, 'Что-то пошло не так 2')

    # Функция, которая позволяет отправить электронное письмо с ответом.  Дожидается ввода
    # от пользователя его эл. адреса, и если все верно, то вызывает функцию в server.py,
    # которая отправляет e-mail.
    @bot.message_handler(func=lambda message: server.db_get_state(message.chat.id, 1) == user_states.States.S_CHOOSE_LOC_MAIL.value)
    def get_mail(message):
        pattern = re.compile(r'[\w.-]+@[\w.-]+\.?[\w]+?')
        result = pattern.findall(message.text)
        if result:
            send_text = server.send_mail(message.chat.id, 1, message.text)
            if send_text:
                bot.send_message(message.chat.id,
                                 'Сообщение отправлено, '
                                 'проверьте письмо во вкладке ' 
                                 'входящих сообщений или спама')
                bot.send_message(message.chat.id,
                                 'Надеюсь мне удалось вам помочь, '
                                 'оцените полученный ответ от 1 до 5')
                server.db_set_state(message.chat.id, 1,
                                    user_states.States.S_FEEDBACK.value)
            else: 
                bot.send_message(message.chat.id, 'Что-то пошло не так')
        else:
            bot.send_message(message.chat.id,
                             'Введен неправильный адрес, попробуйте еще раз')

    # Функция, которая просит пользователя дать оценку работы бота.
    @bot.message_handler(func=lambda message: server.db_get_state(message.chat.id, 1) == user_states.States.S_FEEDBACK.value)
    def get_feedback(message):
        if not message.text.isdigit():
            bot.send_message(message.chat.id, 'Оценка это число от 1 до 5')
            return
        if int(message.text) < 1 or int(message.text) > 5:
            bot.send_message(message.chat.id, 'Оценка это число от 1 до 5')
            return
        else:
            result_feedback = server.get_feedback_db(message.chat.id, 1, message.text)
            if result_feedback:
                bot.send_message(message.chat.id,
                                 'Спасибо за ваш отзыв, можете задавать следующий вопрос')
                server.db_set_state(message.chat.id, 1,
                                    user_states.States.S_QUESTION.value)
            else:
                bot.send_message(message.chat.id, 'Что-то пошло не так 3')

    bot.polling(none_stop=True, interval=1)