import pytz
import time
import random
import logging
import datetime
import requests
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from bs4 import BeautifulSoup

url = "https://www.costco.com.tw/Health-Beauty/Home-Health-Care/Hygiene-Masks-First-Aid/CSD-Medical-Color-Mask-50-Pieces/p/224368"
title = "中衛醫療彩色口罩"
result = False
sent = False
nowtime = None

def send_email():
    global nowtime, sent
    smtp=smtplib.SMTP("smtp.gmail.com", 587)
    smtp.ehlo()
    smtp.starttls()
    smtp.login("sender@gmail.com", "password")
    
    from_addr = "sender@gmail.com"
    to_addr = "receiver@gmail.com"

    s = nowtime.strftime("%Y-%m-%d %H:%M:%S") + "\n" + url
    
    message = MIMEText(s, "plain", "utf-8")
    message["From"] = Header("Python", "utf-8")
    message["To"] = Header(to_addr, "utf-8")
    message["Subject"] = Header("好市多中衛口罩上架", "utf-8")
    
    try:
        status = smtp.sendmail(from_addr, to_addr, message.as_string())
        if status == {}:
            print("傳送成功!")
            sent = True
        else:
            print("傳送失敗!")
    except smtplib.SMTPException:
        print("傳送失敗!")

    smtp.quit()

def search():
    try:
        res = requests.get(url)
        soup = BeautifulSoup(res.text, "lxml")
        # title in res.text
        if (soup.find(id="add-to-cart-button-224368") != None or soup.find(id="addToCartButton") != None):
            return True
    except OSError as e:
        print(e)

    return False

def checktime():
    global nowtime
    if 7 <= nowtime.hour <= 22 and nowtime.minute % 30 < 10:
        return True
    return False

def main():
    global nowtime, result, sent
    logging.basicConfig(level=logging.INFO, format="%(asctime)s, %(levelname)s: %(message)s",
                        datefmt="%Y-%m-%d %H:%M:%S")
    while True:
        nowtime = datetime.datetime.now(pytz.timezone("Asia/Taipei"))
        if checktime():
            result = search()
            if result:
                logging.info(url)
                send_email()
            else:
                logging.info(result)

            if sent:
                time.sleep(1000)
                result = False
                sent = False

        time.sleep(random.random() * 60)

if __name__ == "__main__":
    main()