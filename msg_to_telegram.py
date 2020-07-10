import telegram_integration


# Вызывает функцию отправки сообщения в VK.
def send(telegram_id, message):
    telegram_integration.TelegramBot.bot.send_message(telegram_id, 'Ответ на заданный вопрос: ' + message)