from dotenv import load_dotenv
import os

# بارگذاری متغیرهای محیطی از فایل .env
load_dotenv()

# استفاده از متغیر API_URL
api_url = os.getenv("API_URL")

print(api_url)  # چاپ آدرس API
