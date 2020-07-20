import tokens

from sqlalchemy import create_engine, MetaData, Table


engine = create_engine(f'postgresql://postgres:'
                       f'{tokens.PASSWORD_POSTGRES}@localhost:5432/db_bots', echo=False)

metadata = MetaData(engine)

users = Table('users', metadata, autoload=True)
ans_ques = Table('ans_ques', metadata, autoload=True)
states = Table('states', metadata, autoload=True)

USERS_STATE = users.c.state
USERS_TELEGRAM_USER_ID = users.c.telegram_user_id
USERS_TELEGRAM_USERNAME = users.c.telegram_username
USERS_VK_USER_ID = users.c.vk_user_id
USERS_SLACK_USER_ID = users.c.slack_user_id
USERS_ANSWERS = users.c.answers

ANS_QUES_ANSWER = ans_ques.c.answer
ANS_QUES_QUESTION = ans_ques.c.question

STATES_STATE = states.c.state
STATES_DESCRIPTION = states.c.description

STATE = 'state'
TELEGRAM_USER_ID = 'telegram_user_id'
TELEGRAM_USERNAME = 'telegram_username'
VK_USER_ID = 'vk_user_id'
SLACK_USER_ID = 'slack_user_id'
ANSWERS = 'answers'
USER_MARK = 'user_mark'

START = 'start'
HELP = 'help'
RESET = 'reset'

VK = 'vk'
TELEGRAM = 'telegram'
SLACK = 'slack'
EMAIL = 'почта'

MES_TELEGRAM = 1
MES_VK = 2

SLACK_ID_LEN = 11
VK_ID_LEN = 9

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

RATING_MIN = 1
RATING_MAX = 5

FEEDBACK = 'Спасибо за ваш отзыв, можете задавать следующий вопрос'



