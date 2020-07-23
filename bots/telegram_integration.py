import re

import telebot

import server
from standing import user_states
from standing.constants import *


class TelegramBot(object):
    bot = telebot.TeleBot(tokens.TOKEN_TELEGRAM)

    def __init__(self):

        # /reset для сброса состояния пользователя.
        @self.bot.message_handler(commands=[RESET])
        def reset_state(message):
            self.reset_state(message)

        # Команда /start для начала диалога, есть проверка текущего состояния у пользователя.
        # В зависимости от состояния будет выводиться свое сообщение.
        @self.bot.message_handler(commands=[START])
        def send_welcome(message):
            self.send_welcome(message)

        # Описание команды /help.
        @self.bot.message_handler(commands=[HELP])
        def send_help(message):
            self.send_help(message)

        # Проверка наличия вопроса в базе данных,
        # если таковой имеется вывести поддерживаемые мессенджеры.
        @self.bot.message_handler(func=lambda message: server.db_get_state(message.chat.id, MES_TELEGRAM) == user_states.States.S_QUESTION.value)
        def get_question(message):
            self.get_question(message)

        # Выбор куда отправить ответ на вопрос.
        @self.bot.message_handler(func=lambda message: server.db_get_state(message.chat.id, MES_TELEGRAM) == user_states.States.S_CHOOSE_LOC.value)
        def get_location(message):
            self.get_location(message)

        # Блок кода для ввода VK-id, вызывается в том случае если пользователь хочет получить
        # ответ в VK, но его id нет в базе данных.
        # После получения верного id отправляем ответ.
        @self.bot.message_handler(func=lambda message: server.db_get_state(message.chat.id, MES_TELEGRAM) == user_states.States.S_CHOOSE_LOC_VK.value)
        def get_vk_id(message):
            self.get_vk_id(message)

        # Функция, которая позволяет отправить электронное письмо с ответом.  Дожидается ввода
        # от пользователя его эл. адреса, и если все верно, то вызывает функцию в server.py,
        # которая отправляет e-mail.
        @self.bot.message_handler(func=lambda message: server.db_get_state(message.chat.id, MES_TELEGRAM) == user_states.States.S_CHOOSE_LOC_MAIL.value)
        def get_location_mail(message):
            self.get_location_mail(message)

        @self.bot.message_handler(func=lambda message: server.db_get_state(message.chat.id, MES_TELEGRAM) == user_states.States.S_CHOOSE_LOC_SLACK.value)
        def get_location_slack(message):
            self.get_location_slack(message)

        # Функция, которая просит пользователя дать оценку работы бота.
        @self.bot.message_handler(func=lambda message: server.db_get_state(message.chat.id, MES_TELEGRAM) == user_states.States.S_FEEDBACK.value)
        def get_feedback(message):
            self.get_feedback(message)

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

    def message_sender(self, message, *description):
        for item in description:
            self.bot.send_message(message.chat.id, item)

    def reset_state(self, message):
        server.db_set_state(message.chat.id, MES_TELEGRAM, user_states.States.S_START.value)
        self.bot.send_message(message.chat.id, GO_START_COM)

    def send_welcome(self, message):
        server.new_account_telegram(message.chat.id, message.chat.username)
        state = server.db_get_state(message.chat.id, MES_TELEGRAM)
        description = server.state_start(state)
        self.message_sender(message, description)
        if state == user_states.States.S_START.value:
            server.db_set_state(message.chat.id, MES_TELEGRAM,
                                user_states.States.S_QUESTION.value)

    def send_help(self, message):
        keyboard = self.generate_keyboard(f'/{START}', f'/{HELP}', f'/{RESET}')
        self.bot.send_message(message.chat.id, HELP_DESCRIPTION, reply_markup=keyboard)

    def get_question(self, message):
        detect = server.find_question(message.chat.id, MES_TELEGRAM, message.text)
        if detect:
            self.message_sender(message, ANSWER_FOUND)
            keyboard = self.generate_keyboard(VK, TELEGRAM, SLACK, EMAIL)
            self.bot.send_message(message.chat.id, WHERE_ANSWER, reply_markup=keyboard)
            server.db_set_state(message.chat.id, MES_TELEGRAM,
                                user_states.States.S_CHOOSE_LOC.value)

    def get_location(self, message):
        if message.text.lower() == VK:
            check_vk_id = server.check_vk_id(message.chat.id, MES_TELEGRAM)
            if check_vk_id:
                self.message_sender(message, MESSAGE_SENT, MARK)
                server.db_set_state(message.chat.id, MES_TELEGRAM,
                                    user_states.States.S_FEEDBACK.value)
            else:
                self.message_sender(message, NO_VK_ID)
                server.db_set_state(message.chat.id, MES_TELEGRAM,
                                    user_states.States.S_CHOOSE_LOC_VK.value)
        elif message.text.lower() == TELEGRAM:
            answer = server.send_answer_to_telegram(message.chat.id, MES_TELEGRAM)
            self.message_sender(message, REPLY + answer, MARK)
            server.db_set_state(message.chat.id, MES_TELEGRAM,
                                user_states.States.S_FEEDBACK.value)
        elif message.text.lower() == SLACK:
            check_slack_id = server.check_slack_id(message.chat.id, MES_TELEGRAM)
            if check_slack_id:
                self.message_sender(message, MESSAGE_SENT, MARK)
                server.db_set_state(message.chat.id, MES_TELEGRAM,
                                    user_states.States.S_FEEDBACK.value)
            else:
                self.message_sender(message, NO_SLACK_ID)
                server.db_set_state(message.chat.id, MES_TELEGRAM,
                                    user_states.States.S_CHOOSE_LOC_SLACK.value)
        elif message.text.lower() == EMAIL:
            self.message_sender(message, NO_EMAIL)
            server.db_set_state(message.chat.id, MES_TELEGRAM,
                                user_states.States.S_CHOOSE_LOC_MAIL.value)
        else:
            self.message_sender(message, WHERE_ANSWER)

    def get_vk_id(self, message):
        if not message.text.isdigit() or (len(message.text) < VK_ID_LEN or len(message.text) > VK_ID_LEN):
            self.message_sender(message, WRONG_ID)
        else:
            vk_id_to_db = server.set_vk_db(message.text, message.chat.id)
            if vk_id_to_db:
                check_vk_id = server.check_vk_id(message.chat.id, MES_TELEGRAM)
                if check_vk_id:
                    self.message_sender(message, MESSAGE_SENT, MARK)
                    server.db_set_state(message.chat.id, MES_TELEGRAM,
                                        user_states.States.S_FEEDBACK.value)
            else:
                self.message_sender(message, FAULT)

    def get_location_mail(self, message):
        pattern = re.compile(CHECK_EMAIL)
        result = pattern.findall(message.text)
        if result:
            send_text = server.send_mail(message.chat.id, MES_TELEGRAM, message.text)
            if send_text:
                self.message_sender(message, MESSAGE_SENT, MARK)
                server.db_set_state(message.chat.id, MES_TELEGRAM,
                                    user_states.States.S_FEEDBACK.value)
        else:
            self.message_sender(message, FAULT)

    def get_location_slack(self, message):
        if len(message.text) == SLACK_ID_LEN:
            slack_id_of_db = server.set_slack_id_to_db(message.chat.id, MES_TELEGRAM, message.text)
            if slack_id_of_db:
                self.message_sender(message, MESSAGE_SENT, MARK)
                server.db_set_state(message.chat.id, MES_TELEGRAM,
                                    user_states.States.S_FEEDBACK.value)
        else:
            self.message_sender(message, FAULT)

    def get_feedback(self, message):
        if not message.text.isdigit() or (int(message.text) < RATING_MIN or int(message.text) > RATING_MAX):
            self.message_sender(message, WRONG_MARK)
        else:
            result_feedback = server.get_feedback_db(message.chat.id, MES_TELEGRAM, message.text)
            if result_feedback:
                self.message_sender(message, FEEDBACK)
                server.db_set_state(message.chat.id, MES_TELEGRAM,
                                    user_states.States.S_QUESTION.value)
            else:
                self.message_sender(message, FAULT)
