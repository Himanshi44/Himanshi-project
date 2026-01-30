# Delhi AQI Prediction Chatbot

A chatbot that predicts Air Quality Index (AQI) for Delhi using machine learning.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Get API keys:
   - WAQI API: https://aqicn.org/data-platform/token/
   - OpenWeather API: https://openweathermap.org/api

3. Create `.env` file with your API keys:
```
WAQI_API_KEY=your_waqi_key
OPENWEATHER_API_KEY=your_openweather_key
```

4. Run the application:
```bash
python app.py
```

5. Open browser at `http://localhost:5000`

## Features

- Real-time AQI data from WAQI
- Weather data from OpenWeather
- ML-based AQI prediction
- Interactive chatbot interface

## Example Questions

- "What is the current AQI?"
- "Predict the AQI"
- "What will the air quality be?"
