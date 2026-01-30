import requests
import pandas as pd
from datetime import datetime, timedelta
import time
import os
from config import Config

class HistoricalDataFetcher:
    def __init__(self):
        self.waqi_key = Config.WAQI_API_KEY
        self.openweather_key = Config.OPENWEATHER_API_KEY
        self.coords = Config.DELHI_COORDS
        
    def fetch_waqi_historical(self, days=1095):
        """Fetch historical AQI data from WAQI (last 3 years = ~1095 days)"""
        print(f"Fetching WAQI historical data for {days} days...")
        data_list = []
        
        # WAQI provides historical data through their API
        url = f"https://api.waqi.info/feed/delhi/?token={self.waqi_key}"
        
        try:
            response = requests.get(url)
            data = response.json()
            
            if data['status'] == 'ok' and 'data' in data:
                # Get forecast data if available
                if 'forecast' in data['data']:
                    forecast = data['data']['forecast']['daily']
                    
                    for pollutant in ['pm25', 'pm10', 'o3']:
                        if pollutant in forecast:
                            for entry in forecast[pollutant]:
                                data_list.append({
                                    'date': entry['day'],
                                    'pollutant': pollutant,
                                    'avg': entry['avg'],
                                    'max': entry['max'],
                                    'min': entry['min']
                                })
                
                print(f"Fetched {len(data_list)} WAQI records")
        except Exception as e:
            print(f"Error fetching WAQI historical: {e}")
        
        return pd.DataFrame(data_list) if data_list else None
    
    def fetch_openweather_historical(self, days=1095):
        """Fetch historical weather data"""
        print(f"Fetching OpenWeather historical data...")
        data_list = []
        
        # OpenWeather Historical API (last 5 days with free tier)
        # For full historical data, you'd need a paid plan
        # Using current + forecast as fallback
        
        # Get current and forecast
        try:
            # Current weather
            current_url = f"https://api.openweathermap.org/data/2.5/weather?lat={self.coords['lat']}&lon={self.coords['lon']}&appid={self.openweather_key}&units=metric"
            response = requests.get(current_url)
            current = response.json()
            
            data_list.append({
                'timestamp': datetime.now().isoformat(),
                'temp': current['main']['temp'],
                'humidity': current['main']['humidity'],
                'pressure': current['main']['pressure'],
                'wind_speed': current['wind']['speed'],
                'wind_deg': current['wind'].get('deg', 0),
                'clouds': current['clouds']['all']
            })
            
            # 5-day forecast
            forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?lat={self.coords['lat']}&lon={self.coords['lon']}&appid={self.openweather_key}&units=metric"
            response = requests.get(forecast_url)
            forecast = response.json()
            
            if 'list' in forecast:
                for item in forecast['list']:
                    data_list.append({
                        'timestamp': item['dt_txt'],
                        'temp': item['main']['temp'],
                        'humidity': item['main']['humidity'],
                        'pressure': item['main']['pressure'],
                        'wind_speed': item['wind']['speed'],
                        'wind_deg': item['wind'].get('deg', 0),
                        'clouds': item['clouds']['all']
                    })
            
            print(f"Fetched {len(data_list)} weather records")
        except Exception as e:
            print(f"Error fetching weather historical: {e}")
        
        return pd.DataFrame(data_list) if data_list else None
    
    def fetch_from_openaq(self, days=1095):
        """Fetch data from OpenAQ API (free historical data)"""
        print("Fetching data from OpenAQ...")
        data_list = []
        
        # OpenAQ provides free historical air quality data
        base_url = "https://api.openaq.org/v2/measurements"
        
        date_to = datetime.now()
        date_from = date_to - timedelta(days=days)
        
        params = {
            'city': 'Delhi',
            'country': 'IN',
            'date_from': date_from.strftime('%Y-%m-%d'),
            'date_to': date_to.strftime('%Y-%m-%d'),
            'limit': 10000,
            'page': 1
        }
        
        try:
            response = requests.get(base_url, params=params)
            data = response.json()
            
            if 'results' in data:
                for result in data['results']:
                    data_list.append({
                        'date': result['date']['utc'],
                        'parameter': result['parameter'],
                        'value': result['value'],
                        'unit': result['unit'],
                        'location': result['location']
                    })
                
                print(f"Fetched {len(data_list)} OpenAQ records")
        except Exception as e:
            print(f"Error fetching OpenAQ data: {e}")
        
        return pd.DataFrame(data_list) if data_list else None
    
    def prepare_training_data(self):
        """Prepare and merge all historical data"""
        print("Preparing training data...")
        
        # Fetch from multiple sources
        openaq_data = self.fetch_from_openaq()
        weather_data = self.fetch_openweather_historical()
        
        if openaq_data is None or len(openaq_data) == 0:
            print("No historical data available, generating enhanced synthetic data...")
            return self.generate_enhanced_synthetic_data()
        
        # Process OpenAQ data
        openaq_pivot = openaq_data.pivot_table(
            index='date',
            columns='parameter',
            values='value',
            aggfunc='mean'
        ).reset_index()
        
        # Merge with weather data if available
        if weather_data is not None and len(weather_data) > 0:
            weather_data['date'] = pd.to_datetime(weather_data['timestamp']).dt.date.astype(str)
            weather_agg = weather_data.groupby('date').mean(numeric_only=True)
            
            combined = pd.merge(openaq_pivot, weather_agg, on='date', how='inner')
        else:
            combined = openaq_pivot
        
        # Save raw data
        os.makedirs('data', exist_ok=True)
        combined.to_csv('data/historical_data.csv', index=False)
        print(f"Saved {len(combined)} records to data/historical_data.csv")
        
        return combined
    
    def generate_enhanced_synthetic_data(self):
        """Generate more realistic synthetic data based on Delhi's patterns"""
        print("Generating enhanced synthetic data based on Delhi patterns...")
        
        import numpy as np
        
        np.random.seed(42)
        n_samples = 2000
        
        # Delhi-specific patterns
        dates = pd.date_range(end=datetime.now(), periods=n_samples, freq='D')
        months = dates.month
        
        # Winter (Nov-Feb): High AQI, Low temp
        # Summer (Apr-Jun): Moderate AQI, High temp
        # Monsoon (Jul-Sep): Low AQI, High humidity
        
        data = []
        for i, date in enumerate(dates):
            month = date.month
            
            # Seasonal patterns
            if month in [11, 12, 1, 2]:  # Winter
                temp = np.random.uniform(10, 25)
                pm25 = np.random.uniform(150, 400)
                pm10 = np.random.uniform(200, 500)
                humidity = np.random.uniform(40, 70)
                wind_speed = np.random.uniform(1, 5)
            elif month in [3, 4, 5, 6]:  # Summer
                temp = np.random.uniform(30, 45)
                pm25 = np.random.uniform(80, 200)
                pm10 = np.random.uniform(100, 300)
                humidity = np.random.uniform(20, 50)
                wind_speed = np.random.uniform(3, 10)
            else:  # Monsoon
                temp = np.random.uniform(25, 35)
                pm25 = np.random.uniform(50, 150)
                pm10 = np.random.uniform(70, 200)
                humidity = np.random.uniform(60, 90)
                wind_speed = np.random.uniform(2, 8)
            
            # Calculate AQI (US EPA formula for PM2.5)
            aqi = self.calculate_aqi_from_pm25(pm25)
            
            data.append({
                'date': date.strftime('%Y-%m-%d'),
                'temp': temp,
                'humidity': humidity,
                'pressure': np.random.uniform(1005, 1020),
                'wind_speed': wind_speed,
                'wind_deg': np.random.uniform(0, 360),
                'clouds': np.random.uniform(0, 100),
                'pm25': pm25,
                'pm10': pm10,
                'o3': np.random.uniform(20, 80),
                'no2': np.random.uniform(20, 100),
                'so2': np.random.uniform(5, 40),
                'co': np.random.uniform(0.5, 8),
                'aqi': aqi
            })
        
        df = pd.DataFrame(data)
        os.makedirs('data', exist_ok=True)
        df.to_csv('data/historical_data.csv', index=False)
        print(f"Generated {len(df)} synthetic records with Delhi patterns")
        
        return df
    
    def calculate_aqi_from_pm25(self, pm25):
        """Calculate AQI from PM2.5 using US EPA formula"""
        if pm25 <= 12.0:
            return self.linear_interpolate(pm25, 0, 12.0, 0, 50)
        elif pm25 <= 35.4:
            return self.linear_interpolate(pm25, 12.1, 35.4, 51, 100)
        elif pm25 <= 55.4:
            return self.linear_interpolate(pm25, 35.5, 55.4, 101, 150)
        elif pm25 <= 150.4:
            return self.linear_interpolate(pm25, 55.5, 150.4, 151, 200)
        elif pm25 <= 250.4:
            return self.linear_interpolate(pm25, 150.5, 250.4, 201, 300)
        else:
            return self.linear_interpolate(pm25, 250.5, 500.4, 301, 500)
    
    def linear_interpolate(self, value, low_conc, high_conc, low_aqi, high_aqi):
        """Linear interpolation for AQI calculation"""
        return ((high_aqi - low_aqi) / (high_conc - low_conc)) * (value - low_conc) + low_aqi
