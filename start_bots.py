﻿import threading

from bots import slack_integration
from bots import telegram_integration
from bots import vk_integration


def main():
    thread_telegram = threading.Thread(target=telegram_integration.TelegramBot, args=(),
                                        name='Active Telegram')
    thread_vk = threading.Thread(target=vk_integration.VKBot, args=(),
                                 name='Active VK')
    thread_slack = threading.Thread(target=slack_integration.SlackBot, args=(),
                                    name='Active Slack')

    thread_telegram.start()
    thread_vk.start()
    thread_slack.start()


if __name__ == '__main__':
    main()