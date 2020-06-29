import threading
import telegram_integration, vk_integration

def start_server():
    thread1 = threading.Thread(target=telegram_integration.activate_telegram_bot, args=(), name='Active Telegram')
    thread2 = threading.Thread(target=vk_integration.activate_vk_bot, args=(), name='Active VK')
    thread1.start()
    thread2.start()

start_server()