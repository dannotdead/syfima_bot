from bots import slack_integration


# Вызывает функцию отправки сообщения в VK.
def send(slack_id, message):
    slack_integration.SlackBot.main(slack_id, message)