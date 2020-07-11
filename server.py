import smtplib

import psycopg2
from email.mime.text import MIMEText
from email.header import Header
from sqlalchemy import create_engine, select, update, insert, exists, MetaData, Table

import tokens
import msg_to_vk
import msg_to_telegram
import msg_to_slack


engine = create_engine(f'postgresql://postgres:'
                       f'{tokens.PASSWORD_POSTGRES}@localhost:5432/db_bots', echo=False)

metadata = MetaData(engine)

users = Table('users', metadata, autoload=True)
ans_ques = Table('ans_ques', metadata, autoload=True)

# Получение состояния у пользователя.
def db_get_state(user_id, messanger_id):
    if messanger_id == 1:
        with engine.connect() as conn:
            sql = select([users.c.state]).where(users.c.telegram_user_id == user_id)
            result = conn.execute(sql)
            current_state = result.fetchone()[0]
            return current_state
    if messanger_id == 2:
        with engine.connect() as conn:
            sql = select([users.c.state]).where(users.c.vk_user_id == user_id)
            result = conn.execute(sql)
            current_state = result.fetchone()[0]
            return current_state

# Запись состояния для пользователя.
def db_set_state(user_id, messanger_id, state):
    if messanger_id == 1:
        with engine.connect() as conn:
            sql = update(users).values({'state': state}).where(users.c.telegram_user_id == user_id)
            conn.execute(sql)
    if messanger_id == 2:
        with engine.connect() as conn:
            sql = update(users).values({'state': state}).where(users.c.vk_user_id == user_id)
            conn.execute(sql)

# Создание новой записи в базе данных, если пользователь пишет из телеграма.
def new_account_telegram(user_id):
    with engine.connect() as conn:
        sql = select([users.c.telegram_user_id]).where(users.c.telegram_user_id == user_id)
        result = conn.execute(sql)
        result1 = result.fetchone()[0]
    if result1 is None:
        with engine.connect() as conn:
            sql = insert(users).values({'telegram_user_id': user_id})
            conn.execute(sql)

# Создание новой записи в базе данных, если пользователь пишет из vk.
def new_account_vk(user_id):
    with engine.connect() as conn:
        sql = select([users.c.vk_user_id]).where(users.c.vk_user_id == user_id)
        get_sql = conn.execute(sql)
        result = get_sql.fetchone()[0]
    if result is None:
        with engine.connect() as conn:
            sql = insert(users).values({'vk_user_id': user_id})
            conn.execute(sql)

# Запись нового VK-id, если telegram уже существует.
def get_vk_db(user_id, message):
    with engine.connect() as conn:
        sql = update(users).values({'vk_user_id': user_id}).where(users.c.telegram_user_id == message)
        conn.execute(sql)
        return True

# Проверка в базе данных VK-id пользователя и отправка ответа на вопрос в VK.
def check_vk_id(user_id, messanger_id):
    if messanger_id == 1:
        with engine.connect() as conn:
            sql = select([users.c.vk_user_id]).where(users.c.telegram_user_id == user_id)
            result = conn.execute(sql)
            check_vk_id = result.fetchone()[0]
    if messanger_id == 2:
        with engine.connect() as conn:
            sql = select([users.c.vk_user_id]).where(users.c.vk_user_id == user_id)
            result = conn.execute(sql)
            check_vk_id = result.fetchone()[0]

    if check_vk_id == 0 or check_vk_id is None:
        return False
    else:
        if messanger_id == 1:
            with engine.connect() as conn:
                sql = select([users.c.answers]).where(users.c.telegram_user_id == user_id)
                result = conn.execute(sql)
                answer = result.fetchone()[0]
                msg_to_vk.send(check_vk_id, 'Ответ на заданный вопрос: ' + answer)
                return True
        if messanger_id == 2:
            with engine.connect() as conn:
                sql = select([users.c.answers]).where(users.c.vk_user_id == user_id)
                result = conn.execute(sql)
                answer = result.fetchone()[0]
                msg_to_vk.send(check_vk_id, 'Ответ на заданный вопрос: ' + answer)
                return True

# Проверяет есть ли slack-id пользователя в базе данных.
def check_slack_id(user_id, messanger_id):
    if messanger_id == 1:
        with engine.connect() as conn:
            sql = select([users.c.slack_user_id]).where(users.c.telegram_user_id == user_id)
            result = conn.execute(sql)
            slack_id = result.fetchone()[0]
            if slack_id is None:
                return False
            else:
                send_to_slack(user_id, messanger_id, slack_id)
                return True
    if messanger_id == 2:
        with engine.connect() as conn:
            sql = select([users.c.slack_user_id]).where(users.c.vk_user_id == user_id)
            result = conn.execute(sql)
            slack_id = result.fetchone()[0]
            if slack_id is None:
                return False
            else:
                send_to_slack(user_id, messanger_id, slack_id)
                return True

# Заполняет поле slack-id в базе данных.
def set_slack_id_to_db(user_id, messanger_id, slack_id):
    if messanger_id == 1:
        with engine.connect() as conn:
            sql = update(users).values({'slack_user_id': slack_id}).where(users.c.telegram_user_id == user_id)
            conn.execute(sql)
            result = send_to_slack(user_id, messanger_id, slack_id)
            return result
    if messanger_id == 2:
        with engine.connect() as conn:
            sql = update(users).values({'slack_user_id': slack_id}).where(users.c.vk_user_id == user_id)
            conn.execute(sql)
            result = send_to_slack(user_id, messanger_id, slack_id)
            return result

# Отправка сообщения в slack, пользователю в direct.
def send_to_slack(user_id, messanger_id, slack_id):
    if messanger_id == 1:
        with engine.connect() as conn:
            sql = select([users.c.answers]).where(users.c.telegram_user_id == user_id)
            result = conn.execute(sql)
            answer = result.fetchone()[0]
            msg_to_slack.send(slack_id, answer)
            return True
    if messanger_id == 2:
        with engine.connect() as conn:
            sql = select([users.c.answers]).where(users.c.vk_user_id == user_id)
            result = conn.execute(sql)
            answer = result.fetchone()[0]
            msg_to_slack.send(slack_id, answer)
            return True

# Отправка письма на почту пользователя.
def send_mail(user_id, messanger_id, mail):
    # cursor = db.cursor(buffered=True)
    if messanger_id == 1:
        with engine.connect() as conn:
            sql = select([users.c.answers]).where(users.c.telegram_user_id == user_id)
            result = conn.execute(sql)
            answer = result.fetchone()[0]
    elif messanger_id == 2:
        with engine.connect() as conn:
            sql = select([users.c.answers]).where(users.c.vk_user_id == user_id)
            result = conn.execute(sql)
            answer = result.fetchone()[0]
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
        sql = select([exists().where(ans_ques.c.question.like('%' + message + '%'))])
        result = conn.execute(sql)
        result1 = int(result.fetchone()[0])
    if result1 == 1:
        with engine.connect() as conn:
            sql = select([ans_ques.c.answer]).where(ans_ques.c.question == message)
            answer = conn.execute(sql)
            answer1 = answer.fetchone()[0]
        if messanger_id == 1:
            with engine.connect() as conn:
                sql = update(users).values({'answers': answer1}).where(users.c.telegram_user_id == user_id)
                conn.execute(sql)
                return True
        if messanger_id == 2:
            with engine.connect() as conn:
                sql = update(users).values({'answers': answer1}).where(users.c.vk_user_id == user_id)
                conn.execute(sql)
                return True
    else:
        return False

# Отправка ответа на вопрос от пользователя в telegram.
def send_answer_to_telegram(user_id, messanger_id):
    if messanger_id == 1:
        with engine.connect() as conn:
            sql = select([users.c.answers]).where(users.c.telegram_user_id == user_id)
            result = conn.execute(sql)
            answer = result.fetchone()[0]
        if answer is not None:
            return answer
        else:
            return 'Не найдено'
    if messanger_id == 2:
        with engine.connect() as conn:
            sql = select([users.c.answers]).where(users.c.vk_user_id == user_id)
            result = conn.execute(sql)
            answer = result.fetchone()[0]
        if answer is not None:
            with engine.connect() as conn:
                sql = select([users.c.telegram_user_id]).where(users.c.vk_user_id == user_id)
                result = conn.execute(sql)
                tel_id = result.fetchone()[0]
                msg_to_telegram.send(tel_id, answer)
                return True

# Запись оценки пользователя в базу данных.
def get_feedback_db(user_id, messanger_id, mark):
    if messanger_id == 1:
        with engine.connect() as conn:
            sql = update(users).values({'user_mark': mark}).where(users.c.telegram_user_id == user_id)
            conn.execute(sql)
            return True
    if messanger_id == 2:
        with engine.connect() as conn:
            sql = update(users).values({'user_mark': mark}).where(users.c.vk_user_id == user_id)
            conn.execute(sql)
            return True
