import re
import json

import vk_api
import vk_api.longpoll
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

import tokens
import server
import user_states


class VKBot(object):
    vk_session = vk_api.VkApi(token=tokens.TOKEN_VK)
    session_api = vk_session.get_api()
    longpoll = vk_api.longpoll.VkLongPoll(vk_session)

    def __init__(self):
        self.LIST_HELP = ['/start', '/help', '/reset', ]
        self.LIST_LOCATION = ['VK', 'Telegram', 'Slack', 'Почта', ]
        self.vk_start()

    @classmethod
    def message_sender(cls, id, text, keyboard=''):
        cls.vk_session.method('messages.send', {'user_id': id, 'message': text,
                                                'random_id': 0, 'keyboard': keyboard})

    def get_keyboard(self, buttons):
        keyboard = VkKeyboard(one_time=True)
        for item in buttons:
            keyboard.add_button(item, color=VkKeyboardColor.DEFAULT)
        return keyboard.get_keyboard()

    def vk_start(self):
        for event in self.longpoll.listen():
            if event.type == vk_api.longpoll.VkEventType.MESSAGE_NEW:
                if event.to_me:
                    msg = event.text.lower()
                    id = event.user_id
                    if msg == self.LIST_HELP[0]:
                        server.new_account_vk(event.user_id)
                        state = server.db_get_state(event.user_id, 2)
                        if state == user_states.States.S_START.value:
                            self.message_sender(event.user_id, 'Задайте новый вопрос')
                            server.db_set_state(event.user_id, 2,
                                                user_states.States.S_QUESTION.value)
                        elif state == user_states.States.S_QUESTION.value:
                            self.message_sender(event.user_id,
                                                'Можете задать мне вопрос')
                            self.get_question(event.user_id, event.text)
                        elif state == user_states.States.S_CHOOSE_LOC.value:
                            self.message_sender(event.user_id,
                                                'Вы еще не выбрали куда вам отправить ответ')
                            self.get_location(event.user_id, event.text)
                        elif state == user_states.States.S_CHOOSE_LOC_VK.value:
                            self.message_sender(event.user_id,
                                                'Вы еще не ввели VK-id')
                        elif state == user_states.States.S_CHOOSE_LOC_MAIL.value:
                            self.message_sender(event.user_id,
                                                'Вы еще не ввели свою почту')
                            self.get_location_mail(event.user_id, event.text)
                        elif state == user_states.States.S_CHOOSE_LOC_SLACK.value:
                            self.message_sender(event.user_id,
                                                'Вы еще не ввели свой Slack-id')
                            self.get_location_slack(event.user_id, event.text)
                        elif state == user_states.States.S_FEEDBACK.value:
                            self.message_sender(event.user_id,
                                                'Вы еще не оставили отзыв об ответе')
                            self.get_feedback(event.user_id, event.text)
                        else:
                            self.message_sender(event.user_id,
                                                'Давайте начнем, задайте мне вопрос. '
                                                'Для вызова всех команд используйте /help')
                            server.db_set_state(event.user_id, 2,
                                                user_states.States.S_QUESTION.value)
                    elif msg == self.LIST_HELP[1]:
                        keyboard = self.get_keyboard(self.LIST_HELP)
                        self.message_sender(event.user_id,
                                            '1. /start - начало работы \n'
                                            '2. /help - помощь по командам \n'
                                            '3. /reset - сброс вопроса \n'
                                            'Выберите команду:', keyboard)
                    elif msg == self.LIST_HELP[2]:
                        self.message_sender(event.user_id, 'Задайте новый вопрос')
                        server.db_set_state(event.user_id, 1, user_states.States.S_QUESTION.value)
                    elif msg and server.db_get_state(event.user_id, 2) == user_states.States.S_QUESTION.value:
                        self.get_question(event.user_id, event.text)
                    elif msg and server.db_get_state(event.user_id, 2) == user_states.States.S_CHOOSE_LOC.value:
                        self.get_location(event.user_id, event.text)
                    elif msg and server.db_get_state(event.user_id, 2) == user_states.States.S_CHOOSE_LOC_TELEGRAM.value:
                        self.get_location_telegram(event.user_id, event.text)
                    elif msg and server.db_get_state(event.user_id, 2) == user_states.States.S_CHOOSE_LOC_MAIL.value:
                        self.get_location_mail(event.user_id, event.text)
                    elif msg and server.db_get_state(event.user_id, 2) == user_states.States.S_CHOOSE_LOC_SLACK.value:
                        self.get_location_slack(event.user_id, event.text)
                    elif msg and server.db_get_state(event.user_id, 2) == user_states.States.S_FEEDBACK.value:
                        self.get_feedback(event.user_id, event.text)

    def get_question(self, user_id, text):
        detect = server.find_question(user_id, 2, text)
        if detect:
            keyboard = self.get_keyboard(self.LIST_LOCATION)
            self.message_sender(user_id, 'Ответ на заданный вопрос найден', keyboard)
            self.message_sender(user_id, 'Куда вы хотите чтобы я вам ответил:',)
            server.db_set_state(user_id, 2, user_states.States.S_CHOOSE_LOC.value)

    def get_location(self, user_id, text):
        if text.lower() == 'vk':
            check_vk_id = server.check_vk_id(user_id, 2)
            if check_vk_id:
                self.message_sender(user_id, 'Надеюсь мне удалось вам помочь, '
                                             'оцените полученный ответ от 1 до 5')
                server.db_set_state(user_id, 2,
                                    user_states.States.S_FEEDBACK.value)
            else:
                self.message_sender(user_id, 'Что-то пошло не так')
                server.db_set_state(user_id, 2, user_states.States.S_CHOOSE_LOC_VK.value)
        elif text.lower() == 'telegram':
            telegram_username = server.check_telegram_username(user_id)
            if telegram_username:
                answer = server.send_answer_to_telegram(user_id, 2)
                if answer:
                    self.message_sender(user_id, 'Сообщение отправлено')
                    self.message_sender(user_id, 'Надеюсь мне удалось вам помочь, '
                                                 'оцените полученный ответ от 1 до 5')
                    server.db_set_state(user_id, 2, user_states.States.S_FEEDBACK.value)
                else:
                    self.message_sender(user_id, 'Сообщение НЕ отправлено')
            else:
                url = '@syfimaBot'
                self.message_sender(user_id, f'Введите свое имя пользователя телеграма'
                                             f' и напишите боту {url} /start в телеграме')
                server.db_set_state(user_id, 2, user_states.States.S_CHOOSE_LOC_TELEGRAM.value)
        elif text.lower() == 'slack':
            check_slack_id = server.check_slack_id(user_id, 2)
            if check_slack_id:
                self.message_sender(user_id, 'Сообщение отправлено в Slack')
                self.message_sender(user_id,
                                      'Надеюсь мне удалось вам помочь, '
                                      'оцените полученный ответ от 1 до 5')
                server.db_set_state(user_id, 2,
                                    user_states.States.S_FEEDBACK.value)
            else:
                self.message_sender(user_id,
                                      'Я не знаю ваш Slack-id, напишите его')
                server.db_set_state(user_id, 2,
                                    user_states.States.S_CHOOSE_LOC_SLACK.value)
        elif text.lower() == 'почта':
            self.message_sender(user_id, 'Пожалуйста напишите почту на которую хотите получить ответ')
            server.db_set_state(user_id, 2, user_states.States.S_CHOOSE_LOC_MAIL.value)

    def get_location_telegram(self, user_id, text):
        username = server.set_telegram_username(user_id, text)
        if username:
            self.message_sender(user_id, 'Напишите мне в телеграме, '
                                         'чтобы я смог отправить сообщение '
                                         'и повторите попытку')
            server.db_set_state(user_id, 2,
                                user_states.States.S_CHOOSE_LOC.value)

    def get_location_mail(self, user_id, text):
        pattern = re.compile(r'[\w.-]+@[\w.-]+\.?[\w]+?')
        result = pattern.findall(text)
        if result:
            send_text = server.send_mail(user_id, 2, text)
            if send_text:
                self.message_sender(user_id, 'Сообщение отправлено, '
                                             'проверьте письмо во вкладке '
                                             'входящих сообщений или спама')
                self.message_sender(user_id, 'Надеюсь мне удалось вам помочь, '
                                             'оцените полученный ответ от 1 до 5')
                server.db_set_state(user_id, 2, user_states.States.S_FEEDBACK.value)
            else:
                self.message_sender(user_id, 'Что-то пошло не так')
        else:
            self.message_sender(user_id, 'Введен неправильный адрес, попробуйте еще раз')

    def get_location_slack(self, user_id, text):
        if len(text) == 11:
            slack_id_to_db = server.set_slack_id_to_db(user_id, 2, text)
            if slack_id_to_db:
                self.message_sender(user_id,
                                    'Все верно, отправляю сообщение в Slack')
                self.message_sender(user_id,
                                    'Надеюсь мне удалось вам помочь, '
                                    'оцените полученный ответ от 1 до 5')
                server.db_set_state(user_id, 2,
                                    user_states.States.S_FEEDBACK.value)
            else:
                self.message_sender(user_id, 'Что-то пошло не так')
        else:
            self.message_sender(user_id,
                                'Slack-id - это 11-ти значная послдеовательность ' 
                                'из заглавных латинских букв и цифр')
            return

    def get_feedback(self, user_id, text):
        if not text.isdigit():
            self.message_sender(user_id, 'Оценка это число от 1 до 5')
            return
        if int(text) < 1 or int(text) > 5:
            self.message_sender(user_id, 'Оценка это число от 1 до 5')
            return
        else:
            result_feedback = server.get_feedback_db(user_id, 2, text)
            if result_feedback:
                self.message_sender(user_id, 'Спасибо за ваш отзыв, можете'
                                             ' задавать следующий вопрос')
                server.db_set_state(user_id, 2,
                                    user_states.States.S_QUESTION.value)
            else:
                self.message_sender(user_id, 'Что-то пошло не так 3')
