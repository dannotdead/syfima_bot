import mysql.connector
import tokens
import smtplib
import msg_to_vk
from email.mime.text import MIMEText
from email.header    import Header

db = mysql.connector.connect(
        host='localhost',
        user='root',
        passwd=tokens.passwd_sql,
        port='3306',
        database='db_bot'
)

def call_db(message):
    import_to_db = 'это запись в бд этого сообщения: ' + message.text
    return import_to_db

def new_account_telegram(value, tel_id):
    # прежде чем добавить пользователя нужно сделать проверку на его наличие в БД
    # если его там нет то создаем новую запись
    cursor = db.cursor(buffered=True)
    cursor.execute('SELECT EXISTS (SELECT telegram_user_id FROM users WHERE telegram_user_id = %d)' % tel_id)
    check_tel = int(cursor.fetchone()[0])
    cursor.execute('SELECT EXISTS (SELECT serial_number FROM users WHERE serial_number = %d)' % value)
    check_num = int(cursor.fetchone()[0])

    if check_tel == 1 and check_num == 1:
        return False
    elif check_num == 1 and check_tel == 0:
        sql = 'UPDATE users SET telegram_user_id = %s WHERE serial_number = %s'
        val = (tel_id, value)
        cursor.execute(sql, val)
        db.commit()
        return False
    elif check_num == 0 and check_tel == 0:
        sql = 'INSERT INTO users (serial_number, telegram_user_id) VALUES (%s, %s)'
        val = (value, tel_id)
        cursor.execute(sql, val)
        db.commit()
        return True
    else: 
        return False

def get_serial_number_after_restart(): # установка последнего идентификатора пользователя
    cursor = db.cursor()
    cursor.execute('SELECT serial_number FROM users')
    result = cursor.fetchall()
    return result[-1]

def check_vk_db(mes_id, messanger_id):
    # здесь будет проверка в бд пользователя на наличие там его id VK
    # ЕСЛИ все ок то отправляем сообщение и возвращаем True если его айди нет то возвращаем False
    cursor = db.cursor(buffered=True)
    if messanger_id == 1:
        cursor.execute('SELECT vk_user_id FROM users WHERE telegram_user_id = %d' % mes_id)
        check_vk_id = cursor.fetchone()[0]
    if check_vk_id == None or check_vk_id == 0:
        return False
    else:
        answer = 'Это ответ на ваш вопрос' # здесь находиться ответ на вопрос найденные в БД
        msg_to_vk.send(check_vk_id, answer)
        return True

def check_mail(mes_id, messanger_id):
    cursor = db.cursor(buffered=True)
    if messanger_id == 1:
        cursor.execute('SELECT user_mail FROM users WHERE telegram_user_id = %d' % mes_id)
        check_mail = cursor.fetchone()[0]
    elif messanger_id == 2:
        cursor.execute('SELECT user_mail FROM users WHERE vk_user_id = %d' % mes_id)
        check_mail = cursor.fetchone()[0]
    if check_mail == None or check_mail == 0:
        return False, check_mail
    else:
        return True, check_mail

def send_mail(message):
    msg = MIMEText('Это сообщение от бота на почту', 'plain', 'utf-8')
    msg['Subject'] = Header('msg_from_bot', 'utf-8')
    smtpObj = smtplib.SMTP('smtp.gmail.com', 587)
    # smtpObj.set_debuglevel(1) debug в консоль
    try:
        smtpObj.starttls()
        smtpObj.login(tokens.main_mail, tokens.main_mail_psw)
        smtpObj.sendmail(tokens.main_mail, message, msg.as_string())
        return True
    except Exception:
        return False
    finally:
        smtpObj.quit()

def get_my_id_from_db(id_from_messanger, messanger_id):
    # Метод который возвращает порядковый номер пользователя в базе данных
    cursor = db.cursor(buffered=True)
    if messanger_id == 1: # идентификатор мессенджера 1 - Telegram
        cursor.execute('SELECT serial_number FROM users WHERE telegram_user_id = %d' % id_from_messanger)
        id_from_tel = int(cursor.fetchone()[0])
        return id_from_tel
    elif messanger_id == 2: # идентификатор мессенджера 2 - Vk
        cursor.execute('SELECT serial_number FROM users WHERE vk_user_id = %d' % id_from_messanger)
        id_from_vk = int(cursor.fetchone()[0])
        return id_from_vk

# cursor = db.cursor()

# cursor.execute("CREATE TABLE users (id INT AUTO_INCREMENT PRIMARY KEY, serial_number INT UNIQUE, telegram_user_id INT UNIQUE, vk_user_id INT UNIQUE, user_mail VARCHAR(255))")