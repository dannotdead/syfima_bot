import re

import telebot

import tokens
import server
import user_states


class TelegramBot(object):
    bot = telebot.TeleBot(tokens.TOKEN_TELEGRAM)

    def __init__(self):

        # /reset для сброса состояния пользователя.
        @self.bot.message_handler(commands=['reset'])
        def reset_state(message):
            self.reset_state(message)

        # Команда /start для начала диалога, есть проверка текущего состояния у пользователя.
        # В зависимости от состояния будет выводиться свое сообщение.
        @self.bot.message_handler(commands=['start'])
        def send_welcome(message):
            self.send_welcome(message)

        # Описание команды /help.
        @self.bot.message_handler(commands=['help'])
        def send_help(message):
            self.send_help(message)

        # Проверка наличия вопроса в базе данных,
        # если таковой имеется вывести поддерживаемые мессенджеры.
        @self.bot.message_handler(func=lambda message: server.db_get_state(message.chat.id, 1) == user_states.States.S_QUESTION.value)
        def send_question(message):
            self.send_question(message)

        # Выбор куда отправить ответ на вопрос.
        @self.bot.message_handler(func=lambda message: server.db_get_state(message.chat.id, 1) == user_states.States.S_CHOOSE_LOC.value)
        def send_answer(message):
            self.send_answer(message)

        # Блок кода для ввода VK-id, вызывается в том случае если пользователь хочет получить
        # ответ в VK, но его id нет в базе данных.
        # После получения верного id отправляем ответ.
        @self.bot.message_handler(func=lambda message: server.db_get_state(message.chat.id, 1) == user_states.States.S_CHOOSE_LOC_VK.value)
        def get_vk_id(message):
            self.get_vk_id(message)

        # Функция, которая позволяет отправить электронное письмо с ответом.  Дожидается ввода
        # от пользователя его эл. адреса, и если все верно, то вызывает функцию в server.py,
        # которая отправляет e-mail.
        @self.bot.message_handler(func=lambda message: server.db_get_state(message.chat.id, 1) == user_states.States.S_CHOOSE_LOC_MAIL.value)
        def get_mail(message):
            self.get_mail(message)

        @self.bot.message_handler(func=lambda message: server.db_get_state(message.chat.id, 1) == user_states.States.S_CHOOSE_LOC_SLACK.value)
        def get_slack(message):
            self.get_slack(message)

        # Функция, которая просит пользователя дать оценку работы бота.
        @self.bot.message_handler(func=lambda message: server.db_get_state(message.chat.id, 1) == user_states.States.S_FEEDBACK.value)
        def get_feedback(message):
            self.get_feedback(message)

        # Любой текст не связанный с запросами пользователя обрабатывается здесь.
        # Отчасти бесполезный метод
        # @self.bot.message_handler(content_types=['text'])
        # def get_text_messages(message):
        #     self.bot.send_message(message.chat.id, 'Я тебя не понимаю, '
        #                                            'давай общаться на человеческом языке,'
        #                                            ' можешь, например, вызвать /start')

        self.bot.polling(none_stop=True, interval=1)

    # Функция которая создает клавиатуру с кнопками.
    @classmethod
    def generate_keyboard(cls, *answer):
        keyboard = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True,
                                                     resize_keyboard=True)
        for item in answer:
            button = telebot.types.KeyboardButton(item)
            keyboard.add(button)
        return keyboard

    def reset_state(self, message):
        server.db_set_state(message.chat.id, 1, user_states.States.S_START.value)
        self.bot.send_message(message.chat.id, 'Вызовите команду /start')

    def send_welcome(self, message):
        server.new_account_telegram(message.chat.id)
        state = server.db_get_state(message.chat.id, 1)
        if state == user_states.States.S_START.value:
            self.bot.send_message(message.chat.id, 'Задайте новый вопрос')
            server.db_set_state(message.chat.id, 1,
                                user_states.States.S_QUESTION.value)
        elif state == user_states.States.S_QUESTION.value:
            self.bot.send_message(message.chat.id,
                                  'Можете задать мне вопрос')
        elif state == user_states.States.S_CHOOSE_LOC.value:
            self.bot.send_message(message.chat.id,
                                  'Вы еще не выбрали куда вам отправить ответ')
        elif state == user_states.States.S_CHOOSE_LOC_VK.value:
            self.bot.send_message(message.chat.id,
                                  'Вы еще не ввели VK-id')
        elif state == user_states.States.S_CHOOSE_LOC_SLACK.value:
            self.bot.send_message(message.chat.id,
                                  'Вы еще не ввели Slack-id')
        elif state == user_states.States.S_CHOOSE_LOC_MAIL.value:
            self.bot.send_message(message.chat.id,
                                  'Вы еще не ввели свою почту')
        elif state == user_states.States.S_FEEDBACK.value:
            self.bot.send_message(message.chat.id,
                                  'Вы еще не оставили отзыв об ответе')
        else:
            self.bot.send_message(message.chat.id,
                                  'Давайте начнем, задайте мне вопрос. '
                                  'Для вызова всех команд используйте /help')
            server.db_set_state(message.chat.id, 1,
                                user_states.States.S_QUESTION.value)

    def send_help(self, message):
        keyboard = self.generate_keyboard('/start', '/help', '/reset')
        self.bot.send_message(message.chat.id, '1. /start - начало работы \n'
                                               '2. /help - помощь по командам \n'
                                               '3. /reset - сброс вопроса \n'
                                               'Выберите команду:',
                                                reply_markup=keyboard)

    def send_question(self, message):
        detect = server.find_question(message.chat.id, 1, message.text)
        if detect:
            self.bot.send_message(message.chat.id, 'Ответ на заданный вопрос найден')
            keyboard = self.generate_keyboard('VK', 'Telegram', 'Slack', 'Почта')
            self.bot.send_message(message.chat.id,
                                  'Куда вы хотите чтобы я вам ответил:',
                                   reply_markup=keyboard)
            server.db_set_state(message.chat.id, 1,
                                user_states.States.S_CHOOSE_LOC.value)
        else:
            if message.text == '/help':
                self.send_help(message)
            else:
                self.bot.send_message(message.chat.id,
                                      'Ответ не был найден, попробуйте задать вопрос снова')

    def send_answer(self, message):
        if message.text.lower() == 'vk':
            check_vk_id = server.check_vk_id(message.chat.id, 1)
            if check_vk_id:
                self.bot.send_message(message.chat.id, 'Сообщение отправлено в VK')
                self.bot.send_message(message.chat.id,
                                      'Надеюсь мне удалось вам помочь, '
                                      'оцените полученный ответ от 1 до 5')
                server.db_set_state(message.chat.id, 1,
                                    user_states.States.S_FEEDBACK.value)
            else:
                self.bot.send_message(message.chat.id,
                                      f'Я не знаю ваш VK-id напишите его, '
                                      f'а также разрешите отправлять '
                                      f'мне сообщения в VK в диалоге {tokens.BOT_VK_URL}')
                server.db_set_state(message.chat.id, 1,
                                    user_states.States.S_CHOOSE_LOC_VK.value)
        elif message.text.lower() == 'telegram':
            answer = server.send_answer_to_telegram(message.chat.id, 1)
            self.bot.send_message(message.chat.id, f'Ответ на заданный вопрос: {answer}')
            self.bot.send_message(message.chat.id,
                                  'Надеюсь мне удалось вам помочь, '
                                  'оцените полученный ответ от 1 до 5')
            server.db_set_state(message.chat.id, 1,
                                user_states.States.S_FEEDBACK.value)
        elif message.text.lower() == 'slack':
            check_slack_id = server.check_slack_id(message.chat.id, 1)
            if check_slack_id:
                self.bot.send_message(message.chat.id, 'Сообщение отправлено в Slack')
                self.bot.send_message(message.chat.id,
                                      'Надеюсь мне удалось вам помочь, '
                                      'оцените полученный ответ от 1 до 5')
                server.db_set_state(message.chat.id, 1,
                                    user_states.States.S_FEEDBACK.value)
            else:
                self.bot.send_message(message.chat.id,
                                      'Я не знаю ваш Slack-id, напишите его')
                server.db_set_state(message.chat.id, 1,
                                    user_states.States.S_CHOOSE_LOC_SLACK.value)
        elif message.text.lower() == 'почта':
            self.bot.send_message(message.chat.id,
                                  'Пожалуйста напишите почту на которую хотите получить ответ')
            server.db_set_state(message.chat.id, 1,
                                user_states.States.S_CHOOSE_LOC_MAIL.value)
        else:
            self.bot.send_message(message.chat.id,
                                  'Пожалуйста выберите куда хотите получить ответ: VK, Telegram, Slack, Mail')

    def get_vk_id(self, message):
        if not message.text.isdigit():
            self.bot.send_message(message.chat.id,
                                  'VK-id - это 9-ти значное число, мне нужно число из 9 цифр')
            return
        if len(message.text) < 9 or len(message.text) > 9:
            self.bot.send_message(message.chat.id, 'Ровно 9 цифр пожалуйста')
            return
        else:
            vk_id_to_db = server.get_vk_db(message.text, message.chat.id)
            if vk_id_to_db:
                check_vk_id = server.check_vk_id(message.chat.id, 1)
                if check_vk_id:
                    self.bot.send_message(message.chat.id,
                                          'Все верно, отправляю сообщение в VK')
                    self.bot.send_message(message.chat.id,
                                          'Надеюсь мне удалось вам помочь, '
                                          'оцените полученный ответ от 1 до 5')
                    server.db_set_state(message.chat.id, 1,
                                        user_states.States.S_FEEDBACK.value)
                else:
                    self.bot.send_message(message.chat.id, 'Что-то пошло не так')
            else:
                self.bot.send_message(message.chat.id, 'Что-то пошло не так 2')

    def get_mail(self, message):
        pattern = re.compile(r'[\w.-]+@[\w.-]+\.?[\w]+?')
        result = pattern.findall(message.text)
        if result:
            send_text = server.send_mail(message.chat.id, 1, message.text)
            if send_text:
                self.bot.send_message(message.chat.id, 'Сообщение отправлено, '
                                                       'проверьте письмо во вкладке '
                                                       'входящих сообщений или спама')
                self.bot.send_message(message.chat.id, 'Надеюсь мне удалось вам помочь, '
                                                       'оцените полученный ответ от 1 до 5')
                server.db_set_state(message.chat.id, 1,
                                    user_states.States.S_FEEDBACK.value)
            else:
                self.bot.send_message(message.chat.id, 'Что-то пошло не так')
        else:
            self.bot.send_message(message.chat.id, 'Введен неправильный адрес,'
                                                   ' попробуйте еще раз')

    def get_slack(self, message):
        if len(message.text) == 11:
            slack_id_of_db = server.set_slack_id_to_db(message.chat.id, 1, message.text)
            if slack_id_of_db:
                self.bot.send_message(message.chat.id,
                                      'Все верно, отправляю сообщение в Slack')
                self.bot.send_message(message.chat.id,
                                      'Надеюсь мне удалось вам помочь, '
                                      'оцените полученный ответ от 1 до 5')
                server.db_set_state(message.chat.id, 1,
                                    user_states.States.S_FEEDBACK.value)
            else:
                self.bot.send_message(message.chat.id, 'Что-то пошло не так')
        else:
            self.bot.send_message(message.chat.id,
                                  'Slack-id - это 11-ти значная послдеовательность ' 
                                  'из заглавных латинских букв и цифр')
            return

    def get_feedback(self, message):
        if not message.text.isdigit():
            self.bot.send_message(message.chat.id, 'Оценка это число от 1 до 5')
            return
        if int(message.text) < 1 or int(message.text) > 5:
            self.bot.send_message(message.chat.id, 'Оценка это число от 1 до 5')
            return
        else:
            result_feedback = server.get_feedback_db(message.chat.id, 1, message.text)
            if result_feedback:
                self.bot.send_message(message.chat.id, 'Спасибо за ваш отзыв, можете'
                                                       ' задавать следующий вопрос')
                server.db_set_state(message.chat.id, 1,
                                    user_states.States.S_QUESTION.value)
            else:
                self.bot.send_message(message.chat.id, 'Что-то пошло не так 3')


