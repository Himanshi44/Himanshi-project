import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import joblib
import os
from datetime import datetime, timedelta
from config import Config
from historical_data_fetcher import HistoricalDataFetcher

class AQIPredictor:
    def __init__(self):
        self.model = None
        self.scaler = None
        self.feature_names = ['temp', 'humidity', 'pressure', 'wind_speed', 
                              'wind_deg', 'clouds', 'pm25', 'pm10', 'o3', 
                              'no2', 'so2', 'co', 'month', 'day_of_week', 
                              'is_winter', 'is_monsoon', 'day_of_year',
                              'temp_pm25_interaction', 'wind_pm_interaction']
        self.historical_data = None
        self.recent_aqi_values = []  # Store recent AQI values for lag features
        self.feature_names_path = 'models/feature_names.pkl'  # Store feature names
        self.load_or_create_model()
    
    def load_or_create_model(self):
        """Load existing model or create a new one"""
        os.makedirs('models', exist_ok=True)
        
        if os.path.exists(Config.MODEL_PATH) and os.path.exists(Config.SCALER_PATH):
            self.model = joblib.load(Config.MODEL_PATH)
            self.scaler = joblib.load(Config.SCALER_PATH)
            
            # Load feature names if available
            if os.path.exists(self.feature_names_path):
                self.feature_names = joblib.load(self.feature_names_path)
            
            print("Model loaded successfully")
            print(f"Loaded features: {self.feature_names}")
            
            # Load historical data for trend analysis
            if os.path.exists('data/historical_data.csv'):
                self.historical_data = pd.read_csv('data/historical_data.csv')
                if 'date' in self.historical_data.columns:
                    self.historical_data['date'] = pd.to_datetime(self.historical_data['date'])
                    # Store last 14 days of AQI for lag features
                    recent = self.historical_data.tail(14)
                    if 'aqi' in recent.columns:
                        self.recent_aqi_values = recent['aqi'].tolist()
        else:
            self.train_model_with_real_data()
    
    def add_temporal_features(self, df, date_col='date'):
        """Add temporal features for better predictions"""
        if date_col in df.columns:
            df['date'] = pd.to_datetime(df['date'])
            df['month'] = df['date'].dt.month
            df['day_of_week'] = df['date'].dt.dayofweek
            df['day_of_year'] = df['date'].dt.dayofyear
            
            # Seasonal indicators
            df['is_winter'] = df['month'].isin([11, 12, 1, 2]).astype(int)
            df['is_monsoon'] = df['month'].isin([7, 8, 9]).astype(int)
            df['is_summer'] = df['month'].isin([4, 5, 6]).astype(int)
            
            # Cyclical encoding for month (captures seasonality better)
            df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12)
            df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12)
            
            # Cyclical encoding for day of week
            df['dow_sin'] = np.sin(2 * np.pi * df['day_of_week'] / 7)
            df['dow_cos'] = np.cos(2 * np.pi * df['day_of_week'] / 7)
        
        return df
    
    def add_interaction_features(self, df):
        """Add interaction features that capture relationships"""
        # Temperature and PM2.5 interaction (temperature inversion affects pollution)
        if 'temp' in df.columns and 'pm25' in df.columns:
            df['temp_pm25_interaction'] = df['temp'] * df['pm25']
        
        # Wind and pollution interaction (wind disperses pollution)
        if 'wind_speed' in df.columns and 'pm25' in df.columns:
            df['wind_pm_interaction'] = df['wind_speed'] * df['pm25']
        
        return df
    
    def add_lag_features(self, df):
        """Add lag features from previous days"""
        if 'aqi' in df.columns:
            # Create lag features (previous 1, 3, 7 days)
            df['aqi_lag1'] = df['aqi'].shift(1)
            df['aqi_lag3'] = df['aqi'].shift(3)
            df['aqi_lag7'] = df['aqi'].shift(7)
            
            # Rolling statistics
            df['aqi_rolling_mean_7'] = df['aqi'].rolling(window=7, min_periods=1).mean()
            df['aqi_rolling_std_7'] = df['aqi'].rolling(window=7, min_periods=1).std()
            
            # Fill NaN values with forward fill then backward fill
            df = df.fillna(method='ffill').fillna(method='bfill')
        
        return df
    
    def train_model_with_real_data(self):
        """Train model with enhanced features"""
        print("Training model with enhanced features...")
        
        # Load historical data
        if os.path.exists('data/historical_data.csv'):
            print("Loading existing historical data...")
            df = pd.read_csv('data/historical_data.csv')
        else:
            print("Fetching historical data...")
            fetcher = HistoricalDataFetcher()
            df = fetcher.prepare_training_data()
        
        if df is None or len(df) == 0:
            print("Error: No data available for training")
            return
        
        # Add temporal features
        df = self.add_temporal_features(df)
        
        # Add interaction features
        df = self.add_interaction_features(df)
        
        # Add lag features
        df = self.add_lag_features(df)
        
        print(f"Dataset size: {len(df)} records")
        if 'date' in df.columns:
            print(f"Date range: {df['date'].min()} to {df['date'].max()}")
        
        # Store historical data
        self.historical_data = df.copy()
        
        # Store recent AQI values
        if 'aqi' in df.columns:
            self.recent_aqi_values = df['aqi'].tail(14).tolist()
        
        # Update feature names to include new features
        self.feature_names = ['temp', 'humidity', 'pressure', 'wind_speed', 
                              'wind_deg', 'clouds', 'pm25', 'pm10', 'o3', 
                              'no2', 'so2', 'co', 'month', 'day_of_week', 
                              'is_winter', 'is_monsoon', 'day_of_year',
                              'temp_pm25_interaction', 'wind_pm_interaction',
                              'aqi_lag1', 'aqi_lag3', 'aqi_lag7',
                              'aqi_rolling_mean_7', 'aqi_rolling_std_7']
        
        # Prepare features and target
        available_features = [f for f in self.feature_names if f in df.columns]
        self.feature_names = available_features
        
        print(f"Training with features: {self.feature_names}")
        
        # Handle missing values
        df = df.fillna(df[self.feature_names].mean())
        
        X = df[self.feature_names]
        
        # Create target variable
        if 'aqi' in df.columns:
            y = df['aqi']
        else:
            print("Calculating AQI from PM2.5...")
            y = df['pm25'].apply(self.calculate_aqi_from_pm25)
        
        # Remove any remaining NaN values
        mask = ~(X.isna().any(axis=1) | y.isna())
        X = X[mask]
        y = y[mask]
        
        print(f"Training with {len(X)} valid records")
        
        # Split data (80-20 split)
        split_idx = int(len(X) * 0.8)
        X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
        y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]
        
        # Scale features
        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train Gradient Boosting model with better parameters
        print("Training Gradient Boosting model...")
        self.model = GradientBoostingRegressor(
            n_estimators=500,
            max_depth=6,
            min_samples_split=5,
            min_samples_leaf=2,
            learning_rate=0.01,
            subsample=0.8,
            random_state=42,
            loss='huber',  # More robust to outliers
            alpha=0.9
        )
        self.model.fit(X_train_scaled, y_train)
        
        # Evaluate
        train_score = self.model.score(X_train_scaled, y_train)
        test_score = self.model.score(X_test_scaled, y_test)
        
        print(f"Training R² score: {train_score:.4f}")
        print(f"Testing R² score: {test_score:.4f}")
        
        # Feature importance
        importance = pd.DataFrame({
            'feature': self.feature_names,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
        print("\nTop 10 Feature Importance:")
        print(importance.head(10))
        
        # Save model, scaler, and feature names
        joblib.dump(self.model, Config.MODEL_PATH)
        joblib.dump(self.scaler, Config.SCALER_PATH)
        joblib.dump(self.feature_names, self.feature_names_path)
        print("\nModel trained and saved successfully")
        print(f"Feature names saved: {self.feature_names}")
    
    def calculate_aqi_from_pm25(self, pm25):
        """Calculate AQI from PM2.5 concentration"""
        if pd.isna(pm25):
            return None
        
        breakpoints = [
            (0, 12.0, 0, 50),
            (12.1, 35.4, 51, 100),
            (35.5, 55.4, 101, 150),
            (55.5, 150.4, 151, 200),
            (150.5, 250.4, 201, 300),
            (250.5, 500.4, 301, 500)
        ]
        
        for c_low, c_high, i_low, i_high in breakpoints:
            if c_low <= pm25 <= c_high:
                return ((i_high - i_low) / (c_high - c_low)) * (pm25 - c_low) + i_low
        
        return 500
    
    def predict_for_date(self, current_data, target_date):
        """Predict AQI for a specific future date with lag features"""
        try:
            features = current_data.copy()
            
            # Add temporal features
            features['month'] = target_date.month
            features['day_of_week'] = target_date.weekday()
            features['day_of_year'] = target_date.timetuple().tm_yday
            features['is_winter'] = 1 if target_date.month in [11, 12, 1, 2] else 0
            features['is_monsoon'] = 1 if target_date.month in [7, 8, 9] else 0
            
            days_ahead = (target_date - datetime.now()).days
            
            # Check if model expects lag features
            has_lag_features = any('aqi_lag' in f or 'aqi_rolling' in f for f in self.feature_names)
            
            if has_lag_features:
                # Use recent AQI values for lag features
                if len(self.recent_aqi_values) > 0:
                    features['aqi_lag1'] = self.recent_aqi_values[-1] if len(self.recent_aqi_values) >= 1 else 150
                    features['aqi_lag3'] = self.recent_aqi_values[-3] if len(self.recent_aqi_values) >= 3 else 150
                    features['aqi_lag7'] = self.recent_aqi_values[-7] if len(self.recent_aqi_values) >= 7 else 150
                    features['aqi_rolling_mean_7'] = np.mean(self.recent_aqi_values[-7:]) if len(self.recent_aqi_values) >= 7 else 150
                    features['aqi_rolling_std_7'] = np.std(self.recent_aqi_values[-7:]) if len(self.recent_aqi_values) >= 7 else 30
                else:
                    # Default values if no history
                    features['aqi_lag1'] = 150
                    features['aqi_lag3'] = 150
                    features['aqi_lag7'] = 150
                    features['aqi_rolling_mean_7'] = 150
                    features['aqi_rolling_std_7'] = 30
            
            # Apply seasonal adjustments to weather features
            if features['is_winter']:
                features['pm25'] = features.get('pm25', 100) * (1.2 + np.random.uniform(-0.1, 0.2))
                features['pm10'] = features.get('pm10', 150) * (1.2 + np.random.uniform(-0.1, 0.2))
                features['temp'] = max(10, features.get('temp', 20) - days_ahead * 0.5 + np.random.uniform(-2, 2))
            elif features['is_monsoon']:
                features['pm25'] = features.get('pm25', 100) * (0.7 + np.random.uniform(-0.1, 0.1))
                features['pm10'] = features.get('pm10', 150) * (0.7 + np.random.uniform(-0.1, 0.1))
                features['humidity'] = min(90, features.get('humidity', 70) + np.random.uniform(0, 10))
            else:
                features['pm25'] = features.get('pm25', 100) * (1.0 + np.random.uniform(-0.15, 0.15))
                features['pm10'] = features.get('pm10', 150) * (1.0 + np.random.uniform(-0.15, 0.15))
            
            # Add interaction features
            features['temp_pm25_interaction'] = features.get('temp', 25) * features.get('pm25', 100)
            features['wind_pm_interaction'] = features.get('wind_speed', 3) * features.get('pm25', 100)
            
            # Prepare features for prediction - use only features that model expects
            feature_values = []
            for feature_name in self.feature_names:
                if feature_name in features:
                    feature_values.append(features[feature_name])
                else:
                    # Provide default value for missing features
                    print(f"Warning: Missing feature {feature_name}, using default")
                    feature_values.append(0)
            
            df = pd.DataFrame([feature_values], columns=self.feature_names)
            X_scaled = self.scaler.transform(df)
            
            # Make prediction
            prediction = self.model.predict(X_scaled)[0]
            
            # Add realistic variability based on rolling std
            if has_lag_features and len(self.recent_aqi_values) >= 7:
                variability = np.std(self.recent_aqi_values[-7:])
            else:
                variability = 30
            
            noise = np.random.normal(0, variability * 0.3)
            prediction = prediction + noise
            
            # Apply trending adjustment
            if has_lag_features and len(self.recent_aqi_values) >= 3:
                recent_trend = self.recent_aqi_values[-1] - self.recent_aqi_values[-3]
                trend_factor = recent_trend * 0.2  # Dampen the trend
                prediction += trend_factor
            
            # Bound prediction to realistic range
            prediction = max(30, min(500, prediction))
            
            # Update recent values for next prediction
            if days_ahead == 1:
                self.recent_aqi_values.append(prediction)
                if len(self.recent_aqi_values) > 14:
                    self.recent_aqi_values.pop(0)
            
            return prediction
            
        except Exception as e:
            print(f"Prediction error for date {target_date}: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def predict_next_n_days(self, current_data, n_days=7):
        """Predict AQI for next N days"""
        predictions = []
        
        # Reset recent values to actual recent data
        if self.historical_data is not None and 'aqi' in self.historical_data.columns:
            self.recent_aqi_values = self.historical_data['aqi'].tail(14).tolist()
        
        for i in range(n_days):
            target_date = datetime.now() + timedelta(days=i+1)
            predicted_aqi = self.predict_for_date(current_data, target_date)
            
            if predicted_aqi is not None:
                predictions.append({
                    'date': target_date.strftime('%Y-%m-%d'),
                    'day_name': target_date.strftime('%A'),
                    'aqi': round(predicted_aqi, 1)
                })
        
        return predictions
    
    def get_past_n_days(self, n_days=7):
        """Get past N days AQI from historical data"""
        if self.historical_data is None or len(self.historical_data) == 0:
            return []
        
        past_data = []
        
        for i in range(n_days, 0, -1):
            target_date = datetime.now() - timedelta(days=i)
            
            if 'date' in self.historical_data.columns:
                date_str = target_date.strftime('%Y-%m-%d')
                matching = self.historical_data[
                    self.historical_data['date'].dt.strftime('%Y-%m-%d') == date_str
                ]
                
                if len(matching) > 0:
                    aqi = matching['aqi'].iloc[0] if 'aqi' in matching.columns else None
                    if aqi is None and 'pm25' in matching.columns:
                        aqi = self.calculate_aqi_from_pm25(matching['pm25'].iloc[0])
                    
                    if aqi is not None:
                        past_data.append({
                            'date': date_str,
                            'day_name': target_date.strftime('%A'),
                            'aqi': round(aqi, 1)
                        })
        
        return past_data
    
    def predict(self, data):
        """Predict AQI from input data (for backward compatibility)"""
        return self.predict_for_date(data, datetime.now() + timedelta(days=1))
    
    def get_aqi_category(self, aqi):
        """Get AQI category and health message"""
        if aqi <= 50:
            return "Good", "Air quality is satisfactory, and air pollution poses little or no risk."
        elif aqi <= 100:
            return "Moderate", "Air quality is acceptable. However, there may be a risk for some people, particularly those who are unusually sensitive to air pollution."
        elif aqi <= 150:
            return "Unhealthy for Sensitive Groups", "Members of sensitive groups may experience health effects. The general public is less likely to be affected."
        elif aqi <= 200:
            return "Unhealthy", "Some members of the general public may experience health effects; members of sensitive groups may experience more serious health effects."
        elif aqi <= 300:
            return "Very Unhealthy", "Health alert: The risk of health effects is increased for everyone."
        else:
            return "Hazardous", "Health warning of emergency conditions: everyone is more likely to be affected."
