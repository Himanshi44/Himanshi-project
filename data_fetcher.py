import requests
from config import Config

class DataFetcher:
    def __init__(self):
        self.waqi_key = Config.WAQI_API_KEY
        self.openweather_key = Config.OPENWEATHER_API_KEY
        self.coords = Config.DELHI_COORDS
    
    def get_current_aqi(self):
        """Fetch current AQI from WAQI API"""
        try:
            url = f"https://api.waqi.info/feed/delhi/?token={self.waqi_key}"
            response = requests.get(url)
            data = response.json()
            
            if data['status'] == 'ok':
                return {
                    'aqi': data['data']['aqi'],
                    'pm25': data['data']['iaqi'].get('pm25', {}).get('v', 0),
                    'pm10': data['data']['iaqi'].get('pm10', {}).get('v', 0),
                    'o3': data['data']['iaqi'].get('o3', {}).get('v', 0),
                    'no2': data['data']['iaqi'].get('no2', {}).get('v', 0),
                    'so2': data['data']['iaqi'].get('so2', {}).get('v', 0),
                    'co': data['data']['iaqi'].get('co', {}).get('v', 0)
                }
        except Exception as e:
            print(f"Error fetching WAQI data: {e}")
            return None
    
    def get_weather_data(self):
        """Fetch weather data from OpenWeather API"""
        try:
            url = f"https://api.openweathermap.org/data/2.5/weather?lat={self.coords['lat']}&lon={self.coords['lon']}&appid={self.openweather_key}&units=metric"
            response = requests.get(url)
            data = response.json()
            
            return {
                'temp': data['main']['temp'],
                'humidity': data['main']['humidity'],
                'pressure': data['main']['pressure'],
                'wind_speed': data['wind']['speed'],
                'wind_deg': data['wind'].get('deg', 0),
                'clouds': data['clouds']['all']
            }
        except Exception as e:
            print(f"Error fetching weather data: {e}")
            return None
    
    def get_combined_data(self):
        """Combine AQI and weather data"""
        aqi_data = self.get_current_aqi()
        weather_data = self.get_weather_data()
        
        if aqi_data and weather_data:
            return {**aqi_data, **weather_data}
        return None
