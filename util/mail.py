import smtplib
import datetime as dt
from email.message import EmailMessage

import util.settings as settings

if __name__ == '__main__':
    msg = EmailMessage()
    msg["From"] = "pipryno@gmail.com"
    msg["Subject"] = "Kollector Error"
    msg["To"] = settings.MAIL_TO
    msg.set_content("Error occured, processRunner had to restart Kollector. \n \
        Please check the following error log, master.")
    error_path = settings.DATA_DIR + '_error/error_' + str(dt.datetime.today().strftime('%Y-%m-%d')) + '.txt'
    msg.add_attachment(open(error_path, "r").read(), filename="error_file.txt")

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login("pipryno@gmail.com", "SurubaoParaiso123")
    server.send_message(msg)