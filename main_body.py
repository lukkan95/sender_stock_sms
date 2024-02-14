import requests
from datetime import *
from twilio.rest import Client
import os

STOCK = "TSLA"
COMPANY_NAME = "Tesla"
ALPHAVENTAGE_API_KEY = os.environ.get("ALP_KEY")
ALPHAVENTAGE_PATH = 'https://www.alphavantage.co/query'
API_KEY_NEWS = os.environ.get("AOI_KEY_NEWS")
NEWS_PATH = "https://newsapi.org/v2/everything"
TWILIO_ACC_SID = os.environ.get("TWILIO_ACC_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
NUMBER_OF_RECEIVER = os.environ.get("NUMBER_OF_RECEIVER")
NUMBER_OF_SENDER = os.environ.get("NUMBER_OF_SENDER")


def send_sms(mess):
    client = Client(TWILIO_ACC_SID, TWILIO_AUTH_TOKEN)
    mess = client.messages \
        .create(
        body=mess,
        from_=NUMBER_OF_SENDER,
        to=NUMBER_OF_RECEIVER)

    print(mess.status)
    print(mess.sid)


def get_stock_data():
    params = {
        "apikey": ALPHAVENTAGE_API_KEY,
        "function": "TIME_SERIES_DAILY",
        "symbol": f"{STOCK}",
        "output": "compact",
            }

    response = requests.get(url=ALPHAVENTAGE_PATH, params=params)
    raw_data = response.json()["Time Series (Daily)"]
    return raw_data


data = get_stock_data()
today = date.today()


def get_news():
    params = {
        "apiKey": API_KEY_NEWS,
        "from": str(today - timedelta(days=1)),
        "q": COMPANY_NAME,
        "sortBy": "popularity",
        "language": "en"
            }

    response = requests.get(url=NEWS_PATH, params=params).json()
    return response


def collect_day_from_data(start_day, generated_data):
    day = 1
    while True:
        last_previous_day_of_data = start_day - timedelta(days=day)
        if str(last_previous_day_of_data) in generated_data.keys():
            return last_previous_day_of_data
        else:
            day += 1


last_day_of_data = collect_day_from_data(today, data)
second_last_day_of_data = collect_day_from_data(last_day_of_data, data)

last_data = float(data[f"{last_day_of_data}"]['4. close'])
second_last_data = float(data[f"{second_last_day_of_data}"]['4. close'])

news = get_news()

difference = round(last_data - second_last_data, 2)
news_list = []

if abs(difference) >= 1:
    for elem in news["articles"][0:3]:
        edited_news = f"Headline: {elem['title']}\nBrief:{elem['description']}\n\n"
        news_list.append(edited_news)
    if last_data - second_last_data <= 0:
        message = f"{STOCK}: 🔻{difference}%\n\n{news_list[0]}{news_list[1]}{news_list[2]}"
    else:
        message = f"{STOCK}: 🔺{difference}%\n\n{news_list[0]}{news_list[1]}{news_list[2]}"
    send_sms(message)



