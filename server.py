import smtplib

import mysql.connector
from email.mime.text import MIMEText
from email.header import Header

import tokens
import msg_to_vk


db = mysql.connector.connect(
        host='localhost',
        user='root',
        passwd=tokens.passwd_sql,
        port='3306',
        database='db_bot'
)

# Получение состояния у пользователя.
def db_get_state(user_id, messanger_id):
    if messanger_id == 1:
        cursor = db.cursor()
        sql = 'SELECT state FROM users WHERE telegram_user_id = %s'
        val = (user_id, )
        cursor.execute(sql, val)
        current_state = cursor.fetchone()[0]
        return current_state

# Запись состояния для пользователя.
def db_set_state(user_id, messanger_id, state):
    if messanger_id == 1:
        cursor = db.cursor()
        sql = 'UPDATE users SET state = %s WHERE telegram_user_id = %s'
        val = (state, user_id, )
        cursor.execute(sql, val)
        db.commit()

# Создание новой записи в базе данных, если пользователь пишет из телеграма.
def new_account_telegram(user_id):
    # Прежде чем добавить пользователя нужно сделать проверку на его наличие в БД,
    # если его там нет то создаем новую запись.
    cursor = db.cursor()
    sql = 'SELECT telegram_user_id FROM users WHERE telegram_user_id = %s'
    val = (user_id, )
    cursor.execute(sql, val)
    result = cursor.fetchone()
    if result == 0 or result is None:
        sql = 'INSERT INTO users (telegram_user_id) VALUES (%s)'
        val = (user_id, )
        cursor.execute(sql, val)
        db.commit()

# Запись нового VK-id, если telegram уже существует.
def get_vk_db(user_id, message):
    cursor = db.cursor(buffered=True)
    sql = 'UPDATE users SET vk_user_id = %s WHERE telegram_user_id = %s'
    val = (user_id, message, )
    cursor.execute(sql, val)
    db.commit()
    return True

# Проверка в базе данных VK-id пользователя и отправка ответа на вопрос в VK.
def check_vk_db(user_id, messanger_id):
    # Если все ок, то отправляем сообщение и возвращаем True,
    # если его айди нет, то возвращаем False
    cursor = db.cursor(buffered=True)
    if messanger_id == 1:
        sql = 'SELECT vk_user_id FROM users WHERE telegram_user_id = %s'
        val = (user_id, )
        cursor.execute(sql, val)
        check_vk_id = cursor.fetchone()[0]

    if check_vk_id == 0 or check_vk_id is None:
        return False
    else:
        sql = 'SELECT answers FROM users WHERE telegram_user_id = %s'
        val = (user_id, )
        cursor.execute(sql, val)
        answer = cursor.fetchone()[0]
        msg_to_vk.send(check_vk_id, 'Ответ на заданный вопрос: ' + answer)
        return True

# Отправка письма на почту пользователя.
def send_mail(user_id, messanger_id, mail):
    cursor = db.cursor(buffered=True)
    if messanger_id == 1:
        sql = 'SELECT answers FROM users WHERE telegram_user_id = %s'
        val = (user_id, )
        cursor.execute(sql, val)
        answer = cursor.fetchone()[0]
    elif messanger_id == 2:
        sql = 'SELECT answers FROM users WHERE vk_user_id = %s'
        val = (user_id, )
        cursor.execute(sql, val)
        answer = cursor.fetchone()[0]
    text = str(answer)
    msg = MIMEText(text.encode('utf-8'), 'plain', 'utf-8')
    msg['Subject'] = Header('msg_from_bot', 'utf-8')
    smtpObj = smtplib.SMTP('smtp.gmail.com', 587)
    # smtpObj.set_debuglevel(1) debug в консоль
    try:
        smtpObj.starttls()
        smtpObj.login(tokens.main_mail, tokens.main_mail_psw)
        smtpObj.sendmail(tokens.main_mail, mail, msg.as_string())
        return True
    # except Exception:
    #     return False
    finally:
        smtpObj.quit()

# Нахождение вопроса от пользователя в базе данных
def find_question(user_id, messanger_id, message):
    cursor = db.cursor(buffered=True)
    question = '%' + message + '%'
    sql = 'SELECT EXISTS (SELECT questions FROM answers_on_questions WHERE questions LIKE %s)'
    val = (question, )
    cursor.execute(sql, val)
    result = int(cursor.fetchone()[0])
    if result == 1:
        if messanger_id == 1:
            sql = 'UPDATE users SET answers = ' \
                  '(SELECT answers FROM answers_on_questions WHERE questions = %s) ' \
                  'WHERE telegram_user_id = %s'
            val = (message, user_id)
            cursor.execute(sql, val)
            db.commit()
            return True
        if messanger_id == 2:
            sql = 'UPDATE users SET answers = %s WHERE vk_user_id = %s'
            val = (message, user_id)
            cursor.execute(sql, val)
            db.commit()
            return True
    else:
        return False

# Отправка ответа на вопрос от пользователя в telegram.
def send_answer_to_telegram(user_id, messanger_id):
    cursor = db.cursor(buffered=True)
    if messanger_id == 1:
        cursor.execute('SELECT answers FROM users WHERE telegram_user_id = %d' % user_id)
        answer = cursor.fetchone()[0]
        if answer is not None:
            return answer
        else:
            return 'Не найдено'
    if messanger_id == 2:
        cursor.execute('SELECT answers FROM users WHERE vk_user_id = %d' % user_id)
        answer = cursor.fetchone()[0]
        return answer

# Запись оценки пользователя в базу данных
def get_feedback_db(user_id, messanger_id, mark):
    cursor = db.cursor(buffered=True)
    if messanger_id == 1:
        sql = 'UPDATE users SET user_mark = %s WHERE telegram_user_id = %s'
        val = (mark, user_id, )
        cursor.execute(sql, val)
        db.commit()
        return True

# cursor = db.cursor()
# cursor.execute("ALTER TABLE users ADD COLUMN user_mark VARCHAR(255) AFTER answers")
# cursor.execute("CREATE TABLE users (id INT AUTO_INCREMENT PRIMARY KEY, state VARCHAR(255), telegram_user_id INT UNIQUE, vk_user_id INT UNIQUE, user_mail VARCHAR(255) UNIQUE, answers VARCHAR(255))")
