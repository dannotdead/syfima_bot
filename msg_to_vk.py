import vk_integration


# Вызывает функцию отправки сообщения в VK.
def send(vk_id, message):
    vk_integration.message_sender(vk_id, message)