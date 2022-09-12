import os
import time
import random
import lxml
import json
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from fake_useragent import UserAgent

url = 'https://www.houseoffraser.co.uk/brand/clarks'
ua = UserAgent()
headers = {
    # for anti-crawler
    'User-Agent': ua.random,
    'Referer': 'https://www.houseoffraser.co.uk/'
}
chromedriver = '/usr/local/bin/chromedriver'
options = Options()
options.add_argument("--disable-notifications")
options.add_argument('--disable-gpu') 
options.add_argument('--no-sandbox')
# options.add_argument('--headless')

output = './output'


def baseCrawler(url):
    # 36 items in one page
    urlWithPa = url + '?dppp=36&OrderBy=rank&dcp='
    page = 0
    itemUrls = []
    while True:
        page += 1
        try:
            res = requests.get(urlWithPa + str(page), headers=headers)
        except:
            # we can set a warning here, such as email or line notify
            """ 
            token = ''
            message = 'this a warning...'
            headers = {"Authorization": "Bearer " + token}
            data = {'message': message}
            requests.post("https://notify-api.line.me/api/notify",
                          headers=headers,
                          data=data)
            """
            pass
        soup = BeautifulSoup(res.text, 'lxml')

        hrefs = soup.find_all('a', class_='ProductImageList', href=True)
        for href in hrefs:
            href = url + href['href'].split('/')[3]
            if href not in itemUrls:
                itemUrls.append(href)
            else:
                continue
        time.sleep(random.randint(0, 1))
        # items < 36 = this is the last page, break loop
        if len(hrefs) < 36:
            break
    print(itemUrls)
    return itemUrls


def itemCrawler(itemUrls):
    headers['Referer'] = 'https://www.houseoffraser.co.uk/brand/clarks'
    items = []
    counter = 0
    for url in itemUrls:
        time.sleep(random.randint(0, 1))
        try:
            html = requests.get(url, headers=headers).text
        except:
            pass
        soup = BeautifulSoup(html, 'lxml')
        info = json.loads(
            soup.find('input',
                      type="hidden",
                      attrs={"id": "hdnSegmentProduct"})['value'])
        info['colcode'] = [url]
        for li in soup.find_all('ul', {'class': 'row colourImages'}):
            if len(li) > 1:
                url = url.split('=')[0] + '='
                for a in li.find_all('a'):
                    if (url + a.get('href')[1:] not in info['colcode']):
                        info['colcode'].append(url + a.get('href')[1:])
        info['colour'] = []
        items.append(info)
        counter += 1
    return items


def sizeCrawler(items):
    headers['Referer'] = 'https://www.houseoffraser.co.uk/brand/clarks'
    for item in items:
        counter = 0
        for colcode in item['colcode']:
            time.sleep(random.randint(0, 1))
            if len(item['colcode']) <= 1:
                try:
                    html = requests.get(colcode, headers=headers).text
                    soup = BeautifulSoup(html, 'lxml')
                except:
                    pass
            else:
                try:
                    print(colcode)
                    driver = webdriver.Chrome(chromedriver, options=options)
                    driver.get(colcode)
                    driver.implicitly_wait(10)
                    soup = BeautifulSoup(driver.page_source, 'lxml')
                    wait = WebDriverWait(driver, 100)
                    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="onetrust-accept-btn-handler"]')))
                    driver.find_element_by_xpath('//*[@id="onetrust-accept-btn-handler"]').click()

                except:
                    driver.quit()
                    pass
            
            # print(soup)
            colour = soup.find('span', {'id': 'colourName'})
            item['colour'].append({
                colour.get('id'): colour.text.strip(),
                'availableSize': [],
                'unavailableSize': []
            })
            for ul in soup.find_all('ul', attrs={'id': 'ulSizes'}):
                for li in ul.find_all('li'):
                    if ('greyOut' not in li['class']):
                        item['colour'][counter]['availableSize'].append(
                            li['data-text'])
                    else:
                        item['colour'][counter]['unavailableSize'].append(
                            li['data-text'])
            counter += 1
    return items


def dataOutput(items):
    if not os.path.isdir(output):
        os.makedirs(output)
    for item in items:
        if 'isEnabled' in item:
            del item['isEnabled']
        if 'categoryId' in item:
            del item['categoryId']
        if 'currency' in item:
            del item['currency']
        if 'isFullPrice' in item:
            del item['isFullPrice']
        if 'position' in item:
            del item['position']
        if 'quantity' in item:
            del item['quantity']
        if 'variant' in item:
            del item['variant']
        if 'budgetCurve' in item:
            del item['budgetCurve']
        with open('./output' + '/' + item['sku'] + '.json', 'w') as f:
            json.dump(item, f, indent=4)


if __name__ == '__main__':
    itemUrls = baseCrawler(url)
    item = itemCrawler(itemUrls)
    info = sizeCrawler(item)
    output = dataOutput(info)
