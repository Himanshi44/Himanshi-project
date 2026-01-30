import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    WAQI_API_KEY = os.getenv('WAQI_API_KEY')
    OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY')
    DELHI_COORDS = {'lat': 28.6139, 'lon': 77.2090}
    MODEL_PATH = 'models/aqi_model.pkl'
    SCALER_PATH = 'models/scaler.pkl'
