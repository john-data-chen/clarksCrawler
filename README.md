# 爬取 Clark 皮鞋
## URL: https://www.houseoffraser.co.uk/brand/clarks/
## Output: sku.JSON

# 爬蟲
## 雖然網站搜尋顯示數量可以改網址參數 dppp=300 改為一頁300個，但品項通常沒這麼多，改成300個後因反爬措施無法收到轉址狀態碼，反而一直困在第一頁
## 同型號鞋的不同色也會在類別裡面顯示一個結果
## 輸出以 sku 作為 檔名 (存入DB時的 primary key)，所以輸出筆數比網站顯示數少
## 不同顏色是用網址參數 colcode 作為分隔，但爬取尺寸時只用 requests 會碰到網址已更改但尺寸數據不動的反爬措施，一定要用 selenium chromedriver
## selenium chromedriver 請到 https://chromedriver.chromium.org/home 下載 版本號: 105.0.5195.52 然後放到 /usr/local/bin/chromedriver 這個路徑下
## 或是到 Line 18 自行修改 chromedriver 路徑

# 如何維持爬取資料的正確性和即時性
## 以 Line 13 為例，基本的反制手段，盡量偽裝成人類： header 隨機 user-agent 偽裝成不同瀏覽器 / 加入 Referer / 隨機暫停
## 以 Line 34 為例，使用 Try Except 放警報措施 email / app notify 通知爬取或儲存失敗，
## 建議公司花點錢購買 Proxy pool 的服務，因直接被擋 IP 很常發生，使用免費 Proxy 額外花的時間成本真的沒有省到錢
## 或是使用 AWS / GCP micro service 每次爬取的 IP 是變動的，失敗時也可以用雲端的警報措施


# JSON 欄位說明:
## 刪除 值為 0, Null 或跟分類無關的欄位
## 顏色跟尺寸整理的格式 { 'colour': [ {'colourName': 'Purple', availableSize:[], unavailableSize:[]}] 

# 爬取下來的資料 如何做簡單的 初步 ETL （分性別 / model number / size)

