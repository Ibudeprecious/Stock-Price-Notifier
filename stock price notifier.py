# from bs4 import BeautifulSoup as bs
# import requests as rq
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager as cdm
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from twilio.rest import Client
from dotenv import load_dotenv
import os
import time
from datetime import datetime as dt

load_dotenv()

sid = os.getenv('TWILIO_ACCOUNT_SID')
auth_token = os.getenv('TWILIO_AUTH_TOKEN')
phonenumber = os.getenv('TWILIO_PHONE')

sender = Client(sid,auth_token)


def set_sele():
    service = Service(cdm().install())
    
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-infobars')
    options.add_argument('--start-maximized')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--no-sandbox')
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    options.add_argument('--disable-blink-features=AutomationControlled')

    driver = webdriver.Chrome(options=options, service=service)
    return driver


def get_percent():
    print('Visiting the website...')
    driver = set_sele()
    url = f'https://zse.hr/en/indeks-366/365?isin=HRZB00ICBEX6'
    driver.get(url) #visits the website
    
    print('Waiting for the element to load...')
    try: #this will wait for 10 seconds until the elent shows up, if it doesn't it moves to the next
        percent = WebDriverWait(driver, 10).until(ec.presence_of_element_located((By.CLASS_NAME, "stock-trend")))
        percenttext = percent.text
        print('Element found')
        return percenttext
    except Exception as e:
        print('Element not found')
        print('Error: ', e)
    finally:
        driver.quit()

last_sent_date = None
cached_value = None

while True:
    now = dt.now()
    if now.hour < 7 or (now.hour == 7 and now.minute < 28):
        print("Waiting for 7:28 AM...")
        time.sleep(60)
    elif now.hour == 7 and now.minute == 28 and (last_sent_date != now.date()):
        cached_value = get_percent()
        print("Got value at 7:28 AM:", cached_value)
        #time.sleep(60)  # Wait to avoid fetching multiple times in the same minute
    elif now.hour == 7 and now.minute ==30 and (last_sent_date != now.date()):
        message = sender.messages.create(
            body="Good morning, the stock price has changed by: " + cached_value,
            from_=phonenumber,
            to="+2349012452831"
        )
        print("message has been sent to:", message.to)
        last_sent_date = now.date()
        cached_value = None  # Reset for next day
        time.sleep(60)  # Wait to avoid sending multiple times in the same minute
    else:
        time.sleep(5)

