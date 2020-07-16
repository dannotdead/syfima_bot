import tokens


START = 'start'
HELP = 'help'
RESET = 'reset'

VK = 'vk'
TELEGRAM = 'telegram'
SLACK = 'slack'
EMAIL = 'почта'

GO_START_COM = f'Вызовите команду /{START}'

HELP_DESCRIPTION = '1. /start - начало работы \n' \
				   '2. /help - помощь по командам \n' \
				   '3. /reset - сброс вопроса \n' \
				   'Выберите команду:'

REPLY = 'Ответ: '
ANSWER_FOUND = 'Ответ на заданный вопрос найден'
WHERE_ANSWER = 'Куда вы хотите чтобы я вам ответил'

MESSAGE_SENT = 'Сообщение отправлено'
MARK = 'Надеюсь мне удалось вам помочь, оцените полученный ответ от 1 до 5'

NO_VK_ID = f'Я не знаю ваш VK-id напишите его, ' \
		   f'а также разрешите отправлять ' \
		   f'мне сообщения в VK в диалоге {tokens.BOT_VK_URL}'
NO_TELEGRAM_USER = f'Введите свое имя пользователя телеграма ' \
                   f'и напишите боту {tokens.BOT_TELEGRAM_URL} /start в телеграме'
NO_SLACK_ID = 'Я не знаю ваш Slack-id'
NO_EMAIL = 'Пожалуйста напишите почту, на которую хотите получить ответ'

WRONG_ID = 'Неверный id'
WRONG_MARK = 'Неверная оценка'
FAULT = 'Что-то пошло не так'

FEEDBACK = 'Спасибо за ваш отзыв, можете задавать следующий вопрос'
