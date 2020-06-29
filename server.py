import mysql.connector
import tokens
import smtplib
import msg_to_vk
from email.mime.text import MIMEText
from email.header    import Header

def call_db(message):
    import_to_db = 'это запись в бд этого сообщения: ' + message.text
    return import_to_db

def new_account():
    import_to_db = 'это запись в бд нового пользователя:'

def check_vk_db():
    # здесь будет проверка в бд пользователя на наличие там его id VK
    # ЕСЛИ все ок то отправляем сообщение и возвращаем True если его айди нет то возвращаем False
    vk_id = tokens.my_id_temporary # пока статично потом брать из БД
    check = True # пока проверка пользователя в БД дает True
    answer = 'Это ответ на ваш вопрос' # здесь находиться ответ на вопрос найденные в БД
    if check:
        msg = True # сообщение отправлено
        msg_to_vk.send(vk_id, answer)
    else:
        msg = False # сообщение не отправлено
    return msg

def check_mail():
    import_to_db = 'проверка почты у пользователя'
    # если почта есть вернуть True иначе False

def send_mail(message):
    msg = MIMEText('это сообщение от бота на почту', 'plain', 'utf-8')
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

# db = mysql.connector.connect(
#         host='localhost',
#         user='root',
#         passwd=passwd_sql,
#         port='3306',
#         database='db_bot'
# )