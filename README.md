# 好市多上架自動通知
好市多所販售的中衛口罩在所有銷售通路中相較便宜，但上架時間不定，因此撰寫此爬蟲，自動檢查商品是否上架。

本爬蟲適用所有好市多線上購物之商品，但須事先取得目標商品之商品網址及商品名稱。

## Installation
```
git clone https://github.com/molrobot/CostcoMaskCrawler.git
cd CostcoMaskCrawler
pip install -r requirements.txt
```
## config.json

### LineBot 通知
LineBot的教學資源已有許多人分享，請自行尋找教學並建置。

建置完成後將 LineBot 的 **Channel access token** 填入 config.json 中的對應欄位。

### E-mail 通知
將Gmail帳號密碼填入config.json中的對應欄位，並設定收件者信箱。

如果要使用其他smtp伺服器請自行更改其他相關設定。

### 搜尋間隔時間
預設搜尋間隔時間為10~20秒，若有需要減少系統資源或流量消耗，可自行更改搜尋間隔時間，或將 **continuous** 設為 false，夜間暫停搜尋。

## product.json
依照範例格式填入目標商品資料，輸入網址時可以順便縮短網址，方便瀏覽

https://www.costco.com.tw/p/ + 商品編號

```json
{
    "url": "https://www.costco.com.tw/p/224368",
    "title": "中衛醫療彩色口罩"
}
```

## 執行
```
python crawler.py
```

## 自動加入購物車
加入購物車需要帶入使用者的好市多帳號的cookies資料，暫不新增此功能。

## 自動結帳
為維護所有消費者購物之公平性，不會新增此功能，請使用者收到上架通知後自行上網購買。