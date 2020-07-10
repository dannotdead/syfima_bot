import vk_api
import vk_api.longpoll

import tokens
import server


class VKBot(object):
    vk_session = vk_api.VkApi(token=tokens.token_vk)
    session_api = vk_session.get_api()
    longpoll = vk_api.longpoll.VkLongPoll(vk_session)

    @classmethod
    def message_sender(cls, id, text):
        cls.vk_session.method('messages.send', {'user_id': id, 'message': text,
                                                'random_id': 0})

    def __init__(self):
        for event in self.longpoll.listen():
            if event.type == vk_api.longpoll.VkEventType.MESSAGE_NEW:
                if event.to_me:
                    msg = event.text.lower()
                    id = event.user_id
                    if msg == 'привет':
                        self.message_sender(id, 'Приветствую')