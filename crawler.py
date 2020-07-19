import pytz
import time
import random
import logging
import datetime
import requests
import smtplib
import json
import configparser
from email.mime.text import MIMEText
from email.header import Header
from bs4 import BeautifulSoup

class costco:
    def __init__(self):
        logging.basicConfig(level=logging.INFO, format="%(asctime)s, %(levelname)s: %(message)s", \
                            datefmt="%Y-%m-%d %H:%M:%S")

        config = configparser.RawConfigParser()
        config.read("crawler.config", encoding="utf-8")

        # 設定目標商品
        self.url = config.get("product", "url")
        self.title = config.get("product", "title")
        # 設定信箱
        self.server = config.get("email", "server")
        self.port = config.getint("email", "port")
        self.user = config.get("email", "user")
        self.password = config.get("email", "password")
        self.from_addr = config.get("email", "from_addr")
        self.to_addr = config.get("email", "to_addr")

        # 設定等待時間
        self.next_send_time = config.getint("time", "next_send_time")
        self.next_search_time = config.getint("time", "next_search_time")

        # 設定 user-agent
        self.USER_AGENT_LIST = json.loads(config.get("agent", "user_agent"))

        # 開始執行
        self.start()

    def start(self):
        while True:
            self.nowtime = datetime.datetime.now(pytz.timezone("Asia/Taipei"))
            if self.checktime():
                result = self.search()
                if result:
                    logging.info(self.url)
                    if self.send_email():
                        time.sleep(self.next_send_time)
                else:
                    logging.info(result)
            time.sleep(self.next_search_time)

    def search(self):
        try:
            header = {
                "user-agent": random.choice(self.USER_AGENT_LIST)
            }
            with requests.get(self.url, headers=header) as res:
                soup = BeautifulSoup(res.text, "lxml")
                if (soup.find(id="add-to-cart-button-224368") != None or soup.find(id="addToCartButton") != None):
                    return True
        except OSError as e:
            print(e)

        return False

    def checktime(self):
        if 7 <= self.nowtime.hour <= 22 and self.nowtime.minute % 30 < 30:
            return True
        return False

    def send_email(self):
        text = self.nowtime.strftime("%Y-%m-%d %H:%M:%S") + "\n" + self.url

        message = MIMEText(text, "plain", "utf-8")
        message["From"] = Header("Python Crawler", "utf-8")
        message["To"] = Header(self.to_addr, "utf-8")
        message["Subject"] = Header("好市多中衛口罩上架", "utf-8")

        with smtplib.SMTP(self.server, self.port) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.login(self.user, self.password)
            status = smtp.sendmail(self.from_addr, self.to_addr, message.as_string())
            smtp.quit()
            if status == {}:
                print("傳送成功!")
                return True

        print("傳送失敗!")
        return False

def main():
    csd = costco()


if __name__ == "__main__":
    main()