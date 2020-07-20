import re

import vk_api
import vk_api.longpoll
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

import tokens
import server
from standing import user_states
from standing.constants import *


class VKBot(object):
    vk_session = vk_api.VkApi(token=tokens.TOKEN_VK)
    session_api = vk_session.get_api()
    longpoll = vk_api.longpoll.VkLongPoll(vk_session)

    def __init__(self):
        self.vk_start()

    @classmethod
    def message_sender(cls, id, text, keyboard=''):
        cls.vk_session.method('messages.send', {'user_id': id, 'message': text,
                                                'random_id': 0, 'keyboard': keyboard})

    def get_keyboard(self, *buttons):
        keyboard = VkKeyboard(one_time=True)
        for item in buttons:
            keyboard.add_button(item, color=VkKeyboardColor.DEFAULT)
        return keyboard.get_keyboard()

    def vk_start(self):
        for event in self.longpoll.listen():
            if event.type == vk_api.longpoll.VkEventType.MESSAGE_NEW:
                if event.to_me:
                    msg = event.text.lower()
                    state = server.db_get_state(event.user_id, MES_VK)
                    if msg == f'/{START}':
                        server.new_account_vk(event.user_id)
                        description = server.state_start(state)
                        self.message_sender(event.user_id, description)
                        if state == user_states.States.S_START.value:
                            server.db_set_state(event.user_id, MES_VK,
                                                user_states.States.S_QUESTION.value)
                    elif msg == f'/{HELP}':
                        keyboard = self.get_keyboard(f'/{START}', f'/{HELP}', f'/{RESET}')
                        self.message_sender(event.user_id, HELP_DESCRIPTION, keyboard)
                    elif msg == f'/{RESET}':
                        self.message_sender(event.user_id, GO_START_COM)
                        server.db_set_state(event.user_id, MES_VK, user_states.States.S_QUESTION.value)
                    elif state == user_states.States.S_QUESTION.value:
                        self.get_question(event.user_id, event.text)
                    elif state == user_states.States.S_CHOOSE_LOC.value:
                        self.get_location(event.user_id, event.text)
                    elif state == user_states.States.S_CHOOSE_LOC_TELEGRAM.value:
                        self.get_location_telegram(event.user_id, event.text)
                    elif state == user_states.States.S_CHOOSE_LOC_MAIL.value:
                        self.get_location_mail(event.user_id, event.text)
                    elif state == user_states.States.S_CHOOSE_LOC_SLACK.value:
                        self.get_location_slack(event.user_id, event.text)
                    elif state == user_states.States.S_FEEDBACK.value:
                        self.get_feedback(event.user_id, event.text)

    def get_question(self, user_id, text):
        detect = server.find_question(user_id, MES_VK, text)
        if detect:
            keyboard = self.get_keyboard(VK, TELEGRAM, SLACK, EMAIL)
            self.message_sender(user_id, ANSWER_FOUND, keyboard)
            self.message_sender(user_id, WHERE_ANSWER)
            server.db_set_state(user_id, MES_VK, user_states.States.S_CHOOSE_LOC.value)

    def get_location(self, user_id, text):
        if text.lower() == VK:
            check_vk_id = server.check_vk_id(user_id, MES_VK)
            if check_vk_id:
                self.message_sender(user_id, MARK)
                server.db_set_state(user_id, MES_VK,
                                    user_states.States.S_FEEDBACK.value)
            else:
                self.message_sender(user_id, FAULT)
                server.db_set_state(user_id, MES_VK, user_states.States.S_CHOOSE_LOC_VK.value)
        elif text.lower() == TELEGRAM:
            telegram_username = server.check_telegram_username(user_id)
            if telegram_username:
                answer = server.send_answer_to_telegram(user_id, MES_VK)
                if answer:
                    self.message_sender(user_id, MESSAGE_SENT)
                    self.message_sender(user_id, MARK)
                    server.db_set_state(user_id, MES_VK, user_states.States.S_FEEDBACK.value)
            else:
                self.message_sender(user_id, NO_TELEGRAM_USER)
                server.db_set_state(user_id, MES_VK, user_states.States.S_CHOOSE_LOC_TELEGRAM.value)
        elif text.lower() == SLACK:
            check_slack_id = server.check_slack_id(user_id, MES_VK)
            if check_slack_id:
                self.message_sender(user_id, MESSAGE_SENT)
                self.message_sender(user_id, MARK)
                server.db_set_state(user_id, MES_VK, user_states.States.S_FEEDBACK.value)
            else:
                self.message_sender(user_id, NO_SLACK_ID)
                server.db_set_state(user_id, MES_VK, user_states.States.S_CHOOSE_LOC_SLACK.value)
        elif text.lower() == EMAIL:
            self.message_sender(user_id, NO_EMAIL)
            server.db_set_state(user_id, MES_VK, user_states.States.S_CHOOSE_LOC_MAIL.value)

    def get_location_telegram(self, user_id, text):
        username = server.set_telegram_username(user_id, text)
        if username:
            server.db_set_state(user_id, MES_VK,
                                user_states.States.S_CHOOSE_LOC.value)

    def get_location_mail(self, user_id, text):
        pattern = re.compile(r'[\w.-]+@[\w.-]+\.?[\w]+?')
        result = pattern.findall(text)
        if result:
            send_text = server.send_mail(user_id, MES_VK, text)
            if send_text:
                self.message_sender(user_id, MESSAGE_SENT)
                self.message_sender(user_id, MARK)
                server.db_set_state(user_id, MES_VK, user_states.States.S_FEEDBACK.value)
        else:
            self.message_sender(user_id, FAULT)

    def get_location_slack(self, user_id, text):
        if len(text) == SLACK_ID_LEN:
            slack_id_to_db = server.set_slack_id_to_db(user_id, MES_VK, text)
            if slack_id_to_db:
                self.message_sender(user_id, MESSAGE_SENT)
                self.message_sender(user_id, MARK)
                server.db_set_state(user_id, MES_VK, user_states.States.S_FEEDBACK.value)
        else:
            self.message_sender(user_id, WRONG_ID)

    def get_feedback(self, user_id, text):
        if not text.isdigit() or (int(text) < RATING_MIN or int(text) > RATING_MAX):
            self.message_sender(user_id, WRONG_MARK)
        else:
            result_feedback = server.get_feedback_db(user_id, MES_VK, text)
            if result_feedback:
                self.message_sender(user_id, FEEDBACK)
                server.db_set_state(user_id, MES_VK, user_states.States.S_QUESTION.value)
