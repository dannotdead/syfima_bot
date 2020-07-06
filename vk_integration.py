import vk_api
import vk_api.longpoll

import tokens
import server


vk_session = vk_api.VkApi(token = tokens.token_vk)
session_api = vk_session.get_api()
longpoll = vk_api.longpoll.VkLongPoll(vk_session)

def message_sender(id, text):
    global vk_session
    vk_session.method('messages.send', {'user_id' : id, 'message' : text, 'random_id' : 0})

def activate_vk_bot():
    global longpoll
    for event in longpoll.listen():
        if event.type == vk_api.longpoll.VkEventType.MESSAGE_NEW:
            if event.to_me:
                msg = event.text.lower()
                id = event.user_id
                if msg == 'привет':
                    message_sender(id, 'Приветствую')