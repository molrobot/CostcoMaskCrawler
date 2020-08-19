# 好市多線上購物爬蟲
# python 3.7.6
# encoding=utf-8

import os
import pytz
import time
import random
import logging
import datetime
import requests
import smtplib
import json
from datetime import datetime
from email.mime.text import MIMEText
from email.header import Header
from bs4 import BeautifulSoup
from linebot import LineBotApi
from linebot.models import TextSendMessage
from linebot.exceptions import LineBotApiError

class costco:
    def __init__(self):
        logging.basicConfig(level=logging.INFO, format="%(asctime)s, %(levelname)s: %(message)s", \
                            datefmt="%Y-%m-%d %H:%M:%S")

        configFileName = "config.json"
        if not os.path.isfile(configFileName):
            print("could not find", configFileName)
            exit()

        with open(configFileName, "r", encoding="utf-8") as json_file:
            config = json.load(json_file)

            # 設定目標商品
            self.url = config["product"]["url"]
            self.title = config["product"]["title"]

            # 設定 Line API
            self.line_bot_token = config["line"]["line_bot_channel_access_token"]
            # self.line_bot_secret = config["line"]["line_bot_channel_secret"]

            # 設定信箱
            self.server = config["email"]["server"]
            self.port = config["email"]["port"]
            self.user = config["email"]["user"]
            self.password = config["email"]["password"]
            self.from_addr = config["email"]["from_addr"]
            self.to_addr = config["email"]["to_addr"]

            # 設定等待時間
            self.next_search_time = config["time"]["next_search_time"]
            self.continuous = config["time"]["continuous"]

            # 設定 user-agent
            self.USER_AGENT_LIST = config["agent"]["user-agent"]

        # 檢查網址為商品頁面或分類列表
        # 切割網址取得商品編號
        if self.url.rsplit("/", 2)[1] == "p":
            self.id = self.url.rsplit("/", 1)[1]
        else:
            self.id = None

        self.line_bot_api = LineBotApi(self.line_bot_token)

        self.message = [
            "商品下架通知",
            "商品上架通知(無庫存)",
            "商品上架通知(有庫存)"
        ]

        '''
        商品狀態
        0 :未上架(分類清單中未出現)
        1 :有上架但無庫存(分類清單中有出現或商品網頁存在，但加入購物車按鈕不存在)
        2 :有上架且(可能)有庫存(分類清單中有出現或商品網頁存在，且加入購物車按鈕存在)
        '''
        self.product_status = 0

    def start(self):
        while True:
            self.nowtime = datetime.now(pytz.timezone("Asia/Taipei"))
            if self.check_time():
                result = self.search()
                if result:
                    logging.info(self.url)
                    if self.send_email():
                        time.sleep(self.next_send_time)
                else:
                    logging.info(result)
            time.sleep(random.randint(5, self.next_search_time))

    # 爬取資料，檢查按鈕是否存在
    def search(self):
        header = {
            "user-agent": random.choice(self.USER_AGENT_LIST)
        }
        with requests.get(self.url, headers=header) as res:
            soup = BeautifulSoup(res.text, "lxml")
            '''
            商品頁面存在，可以找到 addToCartButton
            商品頁面不存在則會自動跳回分類列表，若分類列表存在商品，可能可以找到 add-to-cart-button-xxxxxx
            出現"加入購物車"按鈕不代表一定有庫存
            若不知道商品網址或編號，只有商品分類網址跟商品名稱，就直接搜尋名稱，但無法檢查按鈕
            '''
            if self.id != None:
                return (soup.find(id=("add-to-cart-button-" + self.id)) != None or soup.find(id="addToCartButton") != None)
            else:
                return (self.title in res.text)
        return False

    def add_to_cart(self):
        pass

    def checkout(self):
        pass

    # 自訂時間範圍檢查
    def check_time(self):
        if self.continuous:
            return True
        elif 8 <= self.nowtime.hour <= 22:
            return True
        return False

    # 寄信通知
    def send_email(self):
        text = self.nowtime.strftime("%Y-%m-%d %H:%M:%S ") + self.title + "\n" + self.url

        msg = MIMEText(text, "plain", "utf-8")
        msg["From"] = Header("好市多爬蟲", "utf-8")
        msg["To"] = Header(self.to_addr, "utf-8")
        msg["Subject"] = Header(self.message[self.product_status], "utf-8")

        with smtplib.SMTP(self.server, self.port) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.login(self.user, self.password)
            ret = smtp.sendmail(self.from_addr, self.to_addr, msg.as_string())
            if ret == {}:
                logging.info("郵件傳送成功")
                return True
        logging.info("郵件傳送失敗")
        return False

    # 傳line通知
    def send_line(self):
        text = self.message[self.product_status] + "\n" + \
               self.nowtime.strftime("%Y-%m-%d %H:%M:%S") + "\n" + self.title + "\n" + self.url
        
        try:
            self.line_bot_api.broadcast(TextSendMessage(text=text))
        except LineBotApiError as e:
            print(e)

def main():
    csd = costco()
    csd.start()

if __name__ == "__main__":
    main()
