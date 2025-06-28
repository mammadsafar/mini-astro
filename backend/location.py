import pandas as pd
from langchain_openai import ChatOpenAI
from langchain_experimental.agents import create_pandas_dataframe_agent

# from timezonefinder import TimezoneFinder
# مدل سفارشی با API خارجی
import openai

# پیکربندی API سفارشی
openai.api_key = "aa-lx0ACUMXiI9u11BghecrW7SOLnag98S8OR3Vh59GuJMd6YQ3"
openai.api_base = "https://api.avalai.ir/v1"  # جایگزین کن با آدرس درست
# openai.api_base = "https://api.avalapis.ir/v1"  # جایگزین کن با آدرس درست

# گام ۳: ساخت مدل
llm = ChatOpenAI(
    model="gpt-4o-mini",  # یا هر مدل مورد نظر
    temperature=0,
    openai_api_base=openai.api_base,
    openai_api_key=openai.api_key
)




# گام ۱: بارگذاری اکسل
df = pd.read_excel("City.xlsx")

# گام ۲: جدا کردن استان و شهر + lat/lng
df[['Ostan', 'Shahr']] = df['City'].str.split(',', expand=True)
df['Ostan'] = df['Ostan'].str.strip()
df['Shahr'] = df['Shahr'].str.strip()
df[['lat', 'lng']] = df['Coordinates'].str.split(',', expand=True)
df['lat'] = df['lat'].astype(float)
df['lng'] = df['lng'].astype(float)

# print(df)

# گام ۴: تعریف پرامپت
custom_prefix = """
با توجه به داده‌های ورودی کاربر، یک شیء JSON مانند نمونه زیر بساز. فقط در صورتی این کار را انجام بده که تمام اطلاعات ضروری (نام، تاریخ، ساعت، و محل تولد) به طور کامل و قابل‌استخراج باشند.

### ✅ اگر اطلاعات کامل و معتبر بود:
- فقط متن JSON را خروجی بده.
- هیچ متن اضافی قبل یا بعد از JSON ننویس.
- اگر تاریخ تولد به شمسی بود، با استفاده از محاسبه دقیق (و نه تخمینی)، آن را به میلادی تبدیل کن.
- ساعت تولد را از حالت ۱۲ ساعته مثل "عصر" یا "صبح" به حالت ۲۴ ساعته تبدیل کن.
- lat و lng را با تطبیق دقیق استان و شهر از فایل Excel استخراج کن (توجه: فقط یک بار مجاز به خواندن فایل هستی).
- نام و نام خانوادگی را دقیق و بدون خطا به انگلیسی ترجمه کن (مثلاً از رودین رادین به "Roudin Radin").

### ❌ اگر هر کدام از موارد زیر ناقص یا مبهم بود:
- نام یا نام خانوادگی مشخص نبود
- تاریخ تولد ناقص بود
- ساعت تولد گنگ یا نامشخص بود
- محل تولد با فایل مطابقت نداشت یا مشخص نبود

در این صورت فقط کلمه `False` را چاپ کن. هیچ متن یا کاراکتر اضافه دیگری ننویس.

### نمونه JSON خروجی معتبر:
{
    "name": "Mohammad Safarzadeh",
    "year": "2025",
    "month": "03",
    "day": "29",
    "hour": "14",
    "minut": "30",
    "lat": "56.34532435",
    "lng": "32.34532435",
    "city": "Tabas",
    "tz_str": "Asia/Tehran"
}

### ابزارهای در اختیار:
# Tools

## City (فقط یک بار قابل استفاده است)
- برای استخراج lat و lng شهر محل تولد
- این ابزار فقط یک بار مجاز به خواندن فایل اکسل است، بنابراین در استفاده از آن دقت کن

---

اطلاعات ورودی کاربر 👇
""
نام و نام خانوادگی: رودین رادین
تاریخ تولد: 01 فروردین 1404
ساعت تولد: 22:22 عصر
محل تولد: استان - شهر
""




"""

# گام ۵: ساخت agent
agent = create_pandas_dataframe_agent(
    llm,
    df,
    prefix=custom_prefix,
    verbose=True,
    agent_type="openai-tools",  # یا "zero-shot-react-description"
    handle_parsing_errors=True,
    allow_dangerous_code=True  # 👈 اینو اضافه کن
)
# گام ۶: گرفتن منطقه زمانی
# def add_timezone(json_result):
#     import json
#     tf = TimezoneFinder()
#     data = json.loads(json_result)
#     lat = float(data["lat"])
#     lng = float(data["lng"])
#     tz = tf.timezone_at(lat=lat, lng=lng)
#     data["tz_str"] = tz or "Asia/Tehran"
#     return data

# گام ۷: اجرا
query = """
نام و نام خانوادگی: رودین رادین
تاریخ تولد: 01 فروردین 1404
ساعت تولد: 22:22 عصر
محل تولد: یزد - طبس
"""

response = agent.run(query)
# result = add_timezone(response)

print(response)
