import pytest
from dotenv import load_dotenv
import os
load_dotenv()
print("API_URL:", os.getenv("API_URL"))
