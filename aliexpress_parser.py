import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# 🔐 RapidAPI ключ
RAPIDAPI_KEY = "dab4eb95e6mshcd8f292f4318fa6p12085ajsn8143b688081c"

# 🔍 Ключевые слова
keywords = ["Baseus usb cable"]

# 📄 Подключение к Google Таблице
SPREADSHEET_NAME = "AliExpress Turan Market"
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
client = gspread.authorize(creds)
sheet = client.open(SPREADSHEET_NAME).sheet1

def add_product_to_sheet(title, price, url, image_url):
    sheet.append_row([title, price, f"🔗Click & Buy: {url}", f"🔗{image_url}", "✅"])

def get_product(keyword):
    print(f"🔍 Ищем по: {keyword}")
    url = "https://aliexpress-datahub.p.rapidapi.com/item_search"
    
    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": "aliexpress-datahub.p.rapidapi.com"
    }

    params = {
        "q": keyword
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        data = response.json()
        print(f"📥 Ответ от API: {data}")

        products = data.get("result", {}).get("products", [])
        if not products:
            print("❌ Товар не найден")
            return

        first = products[0]
        title = first.get("title", "Без названия")
        price = first.get("target_sale_price", "0")
        product_url = first.get("product_detail_url", "")
        image_url = first.get("image_url", "")

        add_product_to_sheet(title, price, product_url, image_url)
        print(f"✅ Добавлен: {title}")

    except Exception as e:
        print(f"❌ Ошибка: {e}")

# 🚀 Запуск
for keyword in keywords:
    get_product(keyword)

