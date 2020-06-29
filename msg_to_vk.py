import vk_integration

def send(vk_id, message):
    vk_integration.message_sender(vk_id, message)