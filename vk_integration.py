import vk_api 
from vk_api.longpoll import VkLongPoll, VkEventType
from tokens import token_vk

vk_session = vk_api.VkApi(token = token_vk)
session_api = vk_session.get_api()
lonpoll = VkLongPoll(vk_session)

def message_sender(id, text):
    vk_session.method('messages.send', {'user_id' : id, 'message' : text, 'random_id' : 0})

def message_handler(message_text):
    id = message_text
    message = ''
    # clear = 'я получил id:' + id
    # for event in lonpoll.listen():
        # if event.type == VkEventType.MESSAGE_NEW:
            # if event.to_me:
                # message_sender(id, 'Hi man')
    #             message = event.text.lower()
                # if message == '':
    message_sender(id, 'Hi man')
    # vk_session.method('messages.send', {'user_id' : id, 'message' : 'Hi man', 'random_id' : 0})