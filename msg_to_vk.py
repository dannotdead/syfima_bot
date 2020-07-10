import vk_integration


# Вызывает функцию отправки сообщения в VK.
def send(vk_id, message):
    vk_integration.VKBot.message_sender(vk_id, message)