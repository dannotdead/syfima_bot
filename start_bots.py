import threading

import telegram_integration
import vk_integration


def start_server():
    thread1 = threading.Thread(target=telegram_integration.TelegramBot,
                               args=(), name='Active Telegram')
    thread2 = threading.Thread(target=vk_integration.VKBot,
                               args=(), name='Active VK')
    thread1.start()
    thread2.start()


if __name__ == '__main__':
    start_server()