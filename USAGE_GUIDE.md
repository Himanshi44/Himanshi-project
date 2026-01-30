# Delhi AQI Prediction Chatbot - Usage Guide

## 📋 Prerequisites

- Python 3.8 or higher
- Internet connection for API calls
- API keys from WAQI and OpenWeather

---

## 🚀 Step-by-Step Setup

### Step 1: Clone/Download the Project

If you haven't already, download or clone this project to your local machine:
```bash
cd "c:\Users\tanmay\Downloads\himanshy project"
```

### Step 2: Install Dependencies

Open a terminal/command prompt in the project directory and run:

```bash
pip install -r requirements.txt
```

This will install:
- Flask (web framework)
- requests (API calls)
- pandas (data manipulation)
- numpy (numerical operations)
- scikit-learn (machine learning)
- python-dotenv (environment variables)
- joblib (model serialization)

### Step 3: Get API Keys

#### WAQI API Key (World Air Quality Index)
1. Go to https://aqicn.org/data-platform/token/
2. Fill in your details and request a token
3. You'll receive an API key via email (usually instant)
4. Copy the token (format: `abcd1234efgh5678`)

#### OpenWeather API Key
1. Go to https://openweathermap.org/api
2. Sign up for a free account
3. Go to "API keys" in your account dashboard
4. Copy your default API key or create a new one
5. Note: Free tier allows 1,000 calls/day (sufficient for this project)

### Step 4: Configure Environment Variables

1. Copy the example environment file:
```bash
copy .env.example .env
```

Or create a new `.env` file manually with:

```env
WAQI_API_KEY=your_actual_waqi_key_here
OPENWEATHER_API_KEY=your_actual_openweather_key_here
```

2. Replace `your_actual_waqi_key_here` and `your_actual_openweather_key_here` with your actual API keys

**Important:** Never commit the `.env` file to version control!

### Step 5: First Run - Model Training

On first run, the application will automatically:

1. Try to fetch real historical data from OpenAQ API
2. If unavailable, generate enhanced synthetic data based on Delhi's seasonal patterns
3. Train the machine learning model
4. Save the trained model to `models/` directory

Run the application:

```bash
python app.py
```

You should see output like:
```
Training model with real historical data from Delhi...
Fetching data from OpenAQ...
Fetched 5000 OpenAQ records
Dataset size: 2000 records
Date range: 2022-01-01 to 2024-12-31
Training with 1800 valid records
Training R² score: 0.9245
Testing R² score: 0.8876

Feature Importance:
   feature  importance
0    pm25    0.450123
1    pm10    0.285643
2    temp    0.125432
...

Model trained and saved successfully
 * Running on http://0.0.0.0:5000
```

**Note:** Initial model training may take 30-60 seconds depending on your system.

### Step 6: Access the Chatbot

Once you see `Running on http://0.0.0.0:5000`, open your web browser and go to:

```
http://localhost:5000
```

You should see the chatbot interface with a greeting message.

---

## 💬 Using the Chatbot

### Example Queries

#### Get Current AQI
Ask any of these:
- "What is the current AQI?"
- "Current air quality"
- "How's the air today?"
- "AQI now"
- "What's the air quality right now?"
- "Is it safe to go outside?"

**Response Example:**
```
📍 Delhi Air Quality - December 15, 2024 at 02:30 PM

📊 Current AQI: 187
📈 Category: Unhealthy
💡 Health Advice: Everyone may experience health effects.

Current Conditions:
🌡️ Temperature: 28°C
💨 Wind Speed: 3.5 m/s
💧 Humidity: 65%
🔬 PM2.5: 145
🔬 PM10: 220

🚫 Avoid prolonged outdoor activities. Wear a mask if you must go out.
```

#### Get AQI Prediction with Specific Dates
Ask any of these:
- "What will the AQI be tomorrow?"
- "Predict AQI for Friday"
- "Air quality next week"
- "AQI on December 25"
- "What's the AQI in 3 days?"
- "Will the air be good this weekend?"
- "AQI day after tomorrow"
- "Predict air quality for next Monday"

**Response Example:**
```
🔮 AQI Prediction for Delhi - tomorrow

📊 Predicted AQI: 165 (±5)
📈 Expected Category: Unhealthy for Sensitive Groups
💡 Health Advice: Sensitive people should reduce outdoor activity.

Prediction based on current conditions:
🌡️ Temperature: 28°C
💨 Wind Speed: 3.5 m/s
💧 Humidity: 65%
🔬 Current PM2.5: 145

⚠️ Recommendation for tomorrow: Consider indoor exercises. If going out, avoid rush hour traffic.
```

#### Activity-Based Queries
- "Should I go for a run tomorrow?"
- "Is it safe to exercise outside?"
- "Can I cycle today?"
- "Good day for outdoor sports?"

**Response Example:**
```
🏃 Current AQI is 85. Safe for outdoor exercise! Enjoy your workout!
```

#### Compare & Trends
- "Compare today vs tomorrow"
- "Show me the trend"
- "What are the patterns?"
- "AQI history"

**Response Example:**
```
📊 AQI Comparison

Today: 187
Tomorrow (Predicted): 165

📉 Trend: Improving (↓ 22 or -11.8%)
```

#### Natural Language Examples
The chatbot understands natural queries:
- "Will I need a mask on Saturday?"
- "What about air quality in 5 days?"
- "Is the air getting better or worse?"
- "Should I plan outdoor activities for next week?"

#### Get Help
- "Help"
- "What can you do?"

---

## 🔧 Advanced Usage

### Retraining the Model

If you want to retrain the model with fresh data:

1. Delete the existing model files:
```bash
del models\aqi_model.pkl
del models\scaler.pkl
```

2. Optionally delete cached data to fetch fresh data:
```bash
del data\historical_data.csv
```

3. Restart the application:
```bash
python app.py
```

The model will retrain automatically on startup.

### Manual Data Fetch

To manually fetch and save historical data:

```python
from historical_data_fetcher import HistoricalDataFetcher

fetcher = HistoricalDataFetcher()
data = fetcher.prepare_training_data()
print(f"Fetched {len(data)} records")
```

### Checking Model Performance

The training output shows:
- **Training R² score**: How well the model fits training data (higher is better)
- **Testing R² score**: How well it generalizes to new data (0.85+ is good)
- **Feature Importance**: Which factors most affect AQI predictions

---

## 📁 Project Structure

```
himanshy project/
├── app.py                          # Flask application
├── chatbot.py                      # Chatbot logic
├── ml_model.py                     # ML model for predictions
├── data_fetcher.py                 # Real-time API data fetching
├── historical_data_fetcher.py      # Historical data collection
├── config.py                       # Configuration management
├── requirements.txt                # Python dependencies
├── .env                           # API keys (create this)
├── .env.example                   # Example environment file
├── models/                        # Trained ML models
│   ├── aqi_model.pkl             # Saved model
│   └── scaler.pkl                # Feature scaler
├── data/                          # Historical data
│   └── historical_data.csv       # Training dataset
├── templates/                     # HTML templates
│   └── index.html                # Chatbot UI
└── static/                        # Static files
    ├── style.css                 # Styling
    └── script.js                 # Frontend JavaScript
```

---

## 🐛 Troubleshooting

### Issue: API Key Errors

**Error:** `KeyError` or `None` when fetching data

**Solution:**
1. Check your `.env` file exists
2. Verify API keys are correct (no extra spaces)
3. Test API keys:
```bash
# Test WAQI
curl "https://api.waqi.info/feed/delhi/?token=YOUR_KEY"

# Test OpenWeather
curl "https://api.openweathermap.org/data/2.5/weather?lat=28.6139&lon=77.2090&appid=YOUR_KEY"
```

### Issue: Module Not Found

**Error:** `ModuleNotFoundError: No module named 'xyz'`

**Solution:**
```bash
pip install -r requirements.txt --upgrade
```

### Issue: Port Already in Use

**Error:** `Address already in use`

**Solution:**
Change the port in `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5001)  # Changed from 5000
```

### Issue: Model Training Fails

**Error:** Model training produces errors or low scores

**Solution:**
1. Check internet connection for API calls
2. Delete cached data and retry:
```bash
del data\historical_data.csv
```
3. The system will fall back to synthetic data if needed

### Issue: Predictions Are Inaccurate

**Possible Causes:**
- Limited real historical data available
- Using synthetic fallback data
- API rate limits reached

**Solutions:**
1. Run for a few days to collect more data
2. Check API usage limits
3. Consider upgrading to paid API tiers for more historical data

---

## 📊 Understanding AQI Categories

| AQI Range | Category | Color | Health Message |
|-----------|----------|-------|----------------|
| 0-50 | Good | Green | Air quality is satisfactory |
| 51-100 | Moderate | Yellow | Acceptable air quality |
| 101-150 | Unhealthy for Sensitive | Orange | Sensitive groups should limit outdoor activity |
| 151-200 | Unhealthy | Red | Everyone may experience health effects |
| 201-300 | Very Unhealthy | Purple | Health alert for all |
| 301-500 | Hazardous | Maroon | Emergency conditions |

---

## 🔄 Regular Maintenance

### Daily
- Application runs continuously, fetching real-time data

### Weekly
- Monitor model performance
- Check API usage limits

### Monthly
- Retrain model with new historical data
- Review and update if needed

---

## 📞 Support

For issues or questions:
1. Check this guide first
2. Review error messages in the terminal
3. Check API documentation:
   - WAQI: https://aqicn.org/api/
   - OpenWeather: https://openweathermap.org/api

---

## 🎯 Quick Start Checklist

- [ ] Python 3.8+ installed
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] WAQI API key obtained
- [ ] OpenWeather API key obtained
- [ ] `.env` file created with API keys
- [ ] Run `python app.py`
- [ ] Open `http://localhost:5000` in browser
- [ ] Test with "What will the AQI be tomorrow?"

**Congratulations! Your Delhi AQI Prediction Chatbot is ready to use! 🎉**
