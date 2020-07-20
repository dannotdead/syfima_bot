import smtplib

import psycopg2
from email.mime.text import MIMEText
from email.header import Header
from sqlalchemy import select, update, insert, exists

from messages_to import msg_to_vk
from messages_to import msg_to_telegram
from messages_to import msg_to_slack
from standing.constants import *


# Получение состояния у пользователя.
def db_get_state(user_id, messanger_id):
    if messanger_id == MES_TELEGRAM:
        current_state = select_column(USERS_STATE, USERS_TELEGRAM_USER_ID, user_id)
        return current_state
    if messanger_id == MES_VK:
        current_state = select_column(USERS_STATE, USERS_VK_USER_ID, user_id)
        return current_state

# Запись состояния для пользователя.
def db_set_state(user_id, messanger_id, state):
    if messanger_id == MES_TELEGRAM:
        update_column(users, {STATE: state}, USERS_TELEGRAM_USER_ID, user_id)
    if messanger_id == MES_VK:
        update_column(users, {STATE: state}, USERS_VK_USER_ID, user_id)

# Выбирает описание состояния по текущему состоянию при вызове /start.
def state_start(state):
    description = select_column(STATES_DESCRIPTION, STATES_STATE, state)
    return description

# Проверка username-telegram пользователя в бд.
def check_telegram_username(user_id):
    username = select_column(USERS_TELEGRAM_USERNAME, USERS_VK_USER_ID, user_id)
    if username is None:
        return False
    else:
        return True

# Создание новой записи в базе данных, если пользователь пишет из телеграма.
def new_account_telegram(user_id, username):
    with engine.connect() as conn:
        sql = select([USERS_TELEGRAM_USER_ID]).where(USERS_TELEGRAM_USER_ID == user_id)
        sql_name = select([USERS_TELEGRAM_USERNAME]).where(USERS_TELEGRAM_USERNAME == username)
        result = conn.execute(sql)
        result1 = conn.execute(sql_name)
        telegram_user_id = result.fetchone()
        telegram_username = result1.fetchone()
    if telegram_user_id is None and telegram_username is None:
        insert_column(users, {TELEGRAM_USER_ID: user_id, TELEGRAM_USERNAME: username})
    elif telegram_user_id is None:
        update_column(users, {TELEGRAM_USER_ID: user_id}, USERS_TELEGRAM_USERNAME, username)

# Установка username-telegram из vk.
def set_telegram_username(user_id, username):
    update_column(users, {TELEGRAM_USERNAME: username}, USERS_VK_USER_ID, user_id)
    return True

# Создание новой записи в базе данных, если пользователь пишет из vk.
def new_account_vk(user_id):
    vk_user_id = select_column(USERS_VK_USER_ID, USERS_VK_USER_ID, user_id)
    if vk_user_id is None:
        insert_column(users, {VK_USER_ID: user_id})

# Запись нового VK-id, если telegram уже существует.
def set_vk_db(message, user_id):
    update_column(users, {VK_USER_ID: message}, USERS_TELEGRAM_USER_ID, user_id)
    return True

# Проверка в базе данных VK-id пользователя и отправка ответа на вопрос в VK.
def check_vk_id(user_id, messanger_id):
    if messanger_id == MES_TELEGRAM:
        check_vk_id = select_column(USERS_VK_USER_ID, USERS_TELEGRAM_USER_ID, user_id)
    if messanger_id == MES_VK:
        check_vk_id = select_column(USERS_VK_USER_ID, USERS_VK_USER_ID, user_id)

    if check_vk_id == 0 or check_vk_id is None:
        return False
    else:
        _message_to_vk(user_id, messanger_id, check_vk_id)
        return True

# Отправка ответа в VK.
def _message_to_vk(user_id, messanger_id, vk_id):
    if messanger_id == MES_TELEGRAM:
        answer = select_column(USERS_ANSWERS, USERS_TELEGRAM_USER_ID, user_id)
        msg_to_vk.send(vk_id, REPLY + answer)
    if messanger_id == MES_VK:
        answer = select_column(USERS_ANSWERS, USERS_VK_USER_ID, user_id)
        msg_to_vk.send(vk_id, REPLY + answer)

# Проверяет есть ли slack-id пользователя в базе данных.
def check_slack_id(user_id, messanger_id):
    if messanger_id == MES_TELEGRAM:
        slack_id = select_column(USERS_SLACK_USER_ID, USERS_TELEGRAM_USER_ID, user_id)
    if messanger_id == MES_VK:
        slack_id = select_column(USERS_SLACK_USER_ID, USERS_VK_USER_ID, user_id)

    if slack_id is None:
        return False
    else:
        send_to_slack(user_id, messanger_id, slack_id)
        return True

# Заполняет поле slack-id в базе данных.
def set_slack_id_to_db(user_id, messanger_id, slack_id):
    if messanger_id == MES_TELEGRAM:
        update_column(users, {SLACK_USER_ID: slack_id}, USERS_TELEGRAM_USER_ID, user_id)
        send_to_slack(user_id, messanger_id, slack_id)
        return True
    if messanger_id == MES_VK:
        update_column(users, {SLACK_USER_ID: slack_id}, USERS_VK_USER_ID, user_id)
        send_to_slack(user_id, messanger_id, slack_id)
        return True

# Отправка сообщения в slack, пользователю в direct.
def send_to_slack(user_id, messanger_id, slack_id):
    if messanger_id == MES_TELEGRAM:
        answer = select_column(USERS_ANSWERS, USERS_TELEGRAM_USER_ID, user_id)
        msg_to_slack.send(slack_id, answer)
    if messanger_id == MES_VK:
        answer = select_column(USERS_ANSWERS, USERS_VK_USER_ID, user_id)
        msg_to_slack.send(slack_id, answer)

# Отправка письма на почту пользователя.
def send_mail(user_id, messanger_id, mail):
    if messanger_id == MES_TELEGRAM:
        answer = select_column(USERS_ANSWERS, USERS_TELEGRAM_USER_ID, user_id)
    if messanger_id == MES_VK:
        answer = select_column(USERS_ANSWERS, USERS_VK_USER_ID, user_id)
    text = str(answer)
    msg = MIMEText(text.encode('utf-8'), 'plain', 'utf-8')
    msg['Subject'] = Header('msg_from_bot', 'utf-8')
    smtpObj = smtplib.SMTP('smtp.gmail.com', 587)
    # smtpObj.set_debuglevel(1) debug в консоль
    try:
        smtpObj.starttls()
        smtpObj.login(tokens.MAIN_MAIL, tokens.MAIN_MAIL_PSW)
        smtpObj.sendmail(tokens.MAIN_MAIL, mail, msg.as_string())
        return True
    finally:
        smtpObj.quit()

# Нахождение вопроса от пользователя в базе данных.
def find_question(user_id, messanger_id, message):
    with engine.connect() as conn:
        sql = select([exists().where(ans_ques.c.question.like(f'%{message}%'))])
        result = conn.execute(sql)
        output = int(result.fetchone()[0])
    if output == 1:
        answer = select_column(ANS_QUES_ANSWER, ANS_QUES_QUESTION, message)
        if messanger_id == MES_TELEGRAM:
            update_column(users, {ANSWERS: answer}, USERS_TELEGRAM_USER_ID, user_id)
            return True
        if messanger_id == MES_VK:
            update_column(users, {ANSWERS: answer}, USERS_VK_USER_ID, user_id)
            return True
    else:
        return False

# Отправка ответа на вопрос от пользователя в telegram.
def send_answer_to_telegram(user_id, messanger_id):
    if messanger_id == MES_TELEGRAM:
        answer = select_column(USERS_ANSWERS, USERS_TELEGRAM_USER_ID, user_id)
        if answer is not None:
            return answer
        else:
            return FAULT
    if messanger_id == MES_VK:
        answer = select_column(USERS_ANSWERS, USERS_VK_USER_ID, user_id)
        if answer is not None:
            tel_id = select_column(USERS_TELEGRAM_USER_ID, USERS_VK_USER_ID, user_id)
            msg_to_telegram.send(tel_id, answer)
            return True

# Запись оценки пользователя в базу данных.
def get_feedback_db(user_id, messanger_id, mark):
    if messanger_id == MES_TELEGRAM:
        update_column(users, {USER_MARK: mark}, USERS_TELEGRAM_USER_ID, user_id)
        return True
    if messanger_id == MES_VK:
        update_column(users, {USER_MARK: mark}, USERS_VK_USER_ID, user_id)
        return True

# Получить содержимое колонки.
def select_column(search, search_term, condition):
    with engine.connect() as conn:
        sql = select([search]).where(search_term == condition)
        result = conn.execute(sql)
        output = result.fetchone()[0]
        return output

# Обновить содержимое колонки.
def update_column(table, value, search_term, condition):
    with engine.connect() as conn:
        sql = update(table).values(value).where(search_term == condition)
        conn.execute(sql)

# Вставить в таблицу значение.
def insert_column(table, value):
    with engine.connect() as conn:
        sql = insert(table).values(value)
        conn.execute(sql)