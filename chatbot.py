import re
from datetime import datetime, timedelta
from data_fetcher import DataFetcher
from ml_model import AQIPredictor
import dateparser

class AQIChatbot:
    def __init__(self):
        self.data_fetcher = DataFetcher()
        self.predictor = AQIPredictor()
        self.greetings = ['hi', 'hello', 'hey', 'greetings', 'good morning', 'good evening']
        
    def process_message(self, message):
        """Process user message and return response"""
        message_lower = message.lower().strip()
        
        # Greetings
        if any(greet in message_lower for greet in self.greetings):
            return self.get_greeting_response()
        
        # Help
        if 'help' in message_lower or 'what can you' in message_lower:
            return self.get_help_response()
        
        # Current AQI
        if self.is_current_query(message_lower):
            return self.get_current_aqi_response()
        
        # Prediction with date parsing
        if self.is_prediction_query(message_lower):
            target_date = self.extract_date(message)
            return self.get_prediction_response(target_date)
        
        # Comparison queries
        if 'compare' in message_lower or 'vs' in message_lower or 'versus' in message_lower:
            return self.get_comparison_response(message)
        
        # Trend queries
        if 'trend' in message_lower or 'pattern' in message_lower or 'history' in message_lower:
            return self.get_trend_response()
        
        # Graph/Chart request
        if any(word in message_lower for word in ['graph', 'chart', 'trend', 'visualization', 'visual', 'show me']):
            return self.get_graph_response()
        
        # Default - try to understand intent
        return self.get_smart_response(message)
    
    def is_current_query(self, message):
        """Check if query is about current AQI"""
        current_keywords = ['current', 'now', 'today', 'right now', 'at the moment', 
                           'present', 'currently', "what's the", "how's the", 'air quality now']
        return any(keyword in message for keyword in current_keywords)
    
    def is_prediction_query(self, message):
        """Check if query is about prediction"""
        prediction_keywords = ['predict', 'will be', 'would be', 'forecast', 'future', 'tomorrow', 
                              'next', 'later', 'going to be', 'expect', 'anticipated',
                              'coming', 'upcoming', 'ahead', 'aqi on', 'on jan', 'on feb',
                              'on mar', 'on apr', 'on may', 'on jun', 'on jul', 'on aug',
                              'on sep', 'on oct', 'on nov', 'on dec']
        return any(keyword in message for keyword in prediction_keywords)
    
    def extract_date(self, message):
        """Extract date from natural language query"""
        # Use dateparser for natural language date parsing
        parsed_date = dateparser.parse(message, settings={
            'PREFER_DATES_FROM': 'future',
            'RELATIVE_BASE': datetime.now()
        })
        
        if parsed_date:
            return parsed_date
        
        # Parse specific dates like "17th jan", "jan 17", etc.
        current_year = datetime.now().year
        months = {
            'january': 1, 'jan': 1, 'february': 2, 'feb': 2,
            'march': 3, 'mar': 3, 'april': 4, 'apr': 4,
            'may': 5, 'june': 6, 'jun': 6,
            'july': 7, 'jul': 7, 'august': 8, 'aug': 8,
            'september': 9, 'sep': 9, 'sept': 9,
            'october': 10, 'oct': 10, 'november': 11, 'nov': 11,
            'december': 12, 'dec': 12
        }
        
        # Pattern: "17th jan" or "17 january"
        pattern1 = r'(\d{1,2})(?:st|nd|rd|th)?\s+(jan|january|feb|february|mar|march|apr|april|may|june|jun|july|jul|aug|august|sep|sept|september|oct|october|nov|november|dec|december)'
        match = re.search(pattern1, message.lower())
        if match:
            day = int(match.group(1))
            month = months[match.group(2)]
            try:
                target_date = datetime(current_year, month, day)
                if target_date < datetime.now():
                    target_date = datetime(current_year + 1, month, day)
                return target_date
            except ValueError:
                pass
        
        # Pattern: "jan 17" or "january 17"
        pattern2 = r'(jan|january|feb|february|mar|march|apr|april|may|june|jun|july|jul|aug|august|sep|sept|september|oct|october|nov|november|dec|december)\s+(\d{1,2})(?:st|nd|rd|th)?'
        match = re.search(pattern2, message.lower())
        if match:
            month = months[match.group(1)]
            day = int(match.group(2))
            try:
                target_date = datetime(current_year, month, day)
                if target_date < datetime.now():
                    target_date = datetime(current_year + 1, month, day)
                return target_date
            except ValueError:
                pass
        
        # Fallback: check for specific patterns
        message_lower = message.lower()
        
        # Tomorrow
        if 'tomorrow' in message_lower:
            return datetime.now() + timedelta(days=1)
        
        # Day after tomorrow
        if 'day after tomorrow' in message_lower or 'overmorrow' in message_lower:
            return datetime.now() + timedelta(days=2)
        
        # Next week
        if 'next week' in message_lower:
            return datetime.now() + timedelta(days=7)
        
        # This weekend
        if 'weekend' in message_lower or 'saturday' in message_lower:
            days_ahead = (5 - datetime.now().weekday()) % 7
            if days_ahead == 0:
                days_ahead = 7
            return datetime.now() + timedelta(days=days_ahead)
        
        # Specific day names
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        for i, day in enumerate(days):
            if day in message_lower:
                current_day = datetime.now().weekday()
                days_ahead = (i - current_day) % 7
                if days_ahead == 0:
                    days_ahead = 7
                return datetime.now() + timedelta(days=days_ahead)
        
        # Number of days ahead (e.g., "in 3 days", "3 days from now")
        days_match = re.search(r'(?:in\s+)?(\d+)\s+days?', message_lower)
        if days_match:
            days = int(days_match.group(1))
            return datetime.now() + timedelta(days=days)
        
        # Hours ahead
        hours_match = re.search(r'(?:in\s+)?(\d+)\s+hours?', message_lower)
        if hours_match:
            hours = int(hours_match.group(1))
            return datetime.now() + timedelta(hours=hours)
        
        # Default to tomorrow if it's clearly a future query
        if any(word in message_lower for word in ['will', 'going to', 'future', 'next']):
            return datetime.now() + timedelta(days=1)
        
        return None
    
    def get_greeting_response(self):
        """Return greeting message"""
        return """Hello! 👋 I'm your Delhi AQI prediction assistant.

I can help you with:
• Current air quality - "What's the AQI now?"
• Future predictions - "What will the AQI be tomorrow?"
• Specific dates - "AQI on Friday" or "Predict AQI for December 25"
• Time-based queries - "AQI in 3 days" or "Air quality next week"

Just ask me naturally! 😊"""
    
    def get_help_response(self):
        """Return help message"""
        return """🤖 Here's what I can understand:

**Current AQI:**
• "What's the current AQI?"
• "How's the air quality today?"
• "AQI right now"

**Predictions:**
• "What will the AQI be tomorrow?"
• "Predict AQI for Friday"
• "Air quality next week"
• "AQI on December 25"
• "What's the AQI in 3 days?"

**Smart Queries:**
• "Will the air be good this weekend?"
• "Should I go for a run tomorrow?"
• "Is it safe to go outside today?"

Try asking me anything about Delhi's air quality!"""
    
    def get_current_aqi_response(self):
        """Get current AQI information"""
        data = self.data_fetcher.get_combined_data()
        
        if not data:
            return "Sorry, I couldn't fetch the current AQI data. Please try again later."
        
        aqi = data.get('aqi', 0)
        category, message = self.predictor.get_aqi_category(aqi)
        
        current_time = datetime.now().strftime('%B %d, %Y at %I:%M %p')
        
        response = f"📍 **Delhi Air Quality - {current_time}**\n\n"
        response += f"📊 **Current AQI**: {aqi:.0f}\n"
        response += f"📈 **Category**: {category}\n"
        response += f"💡 **Health Advice**: {message}\n\n"
        response += f"**Current Conditions:**\n"
        response += f"🌡️ Temperature: {data.get('temp', 'N/A')}°C\n"
        response += f"💨 Wind Speed: {data.get('wind_speed', 'N/A')} m/s\n"
        response += f"💧 Humidity: {data.get('humidity', 'N/A')}%\n"
        response += f"🔬 PM2.5: {data.get('pm25', 'N/A')}\n"
        response += f"🔬 PM10: {data.get('pm10', 'N/A')}"
        
        # Add contextual advice
        response += f"\n\n{self.get_contextual_advice(aqi, category)}"
        
        return response
    
    def get_prediction_response(self, target_date=None):
        """Get AQI prediction for specific date"""
        data = self.data_fetcher.get_combined_data()
        
        if not data:
            return "Sorry, I couldn't fetch data for prediction. Please try again later."
        
        # Default to tomorrow if no date specified
        if target_date is None:
            target_date = datetime.now() + timedelta(days=1)
        
        days_ahead = (target_date - datetime.now()).days
        hours_ahead = (target_date - datetime.now()).total_seconds() / 3600
        
        # Use the improved date-specific prediction
        predicted_aqi = self.predictor.predict_for_date(data, target_date)
        
        if predicted_aqi is None:
            return "Sorry, prediction failed. Please try again."
        
        # Reduce uncertainty for better accuracy
        uncertainty = min(days_ahead * 3, 25)
        
        category, health_message = self.predictor.get_aqi_category(predicted_aqi)
        
        # Format the date
        if days_ahead == 0 and hours_ahead < 24:
            date_str = f"in {int(hours_ahead)} hours"
        elif days_ahead == 1:
            date_str = "tomorrow"
        elif days_ahead == 2:
            date_str = "day after tomorrow"
        else:
            date_str = target_date.strftime('%A, %B %d, %Y')
        
        response = f"🔮 **AQI Prediction for Delhi - {date_str}**\n\n"
        response += f"📊 **Predicted AQI**: {predicted_aqi:.0f}"
        
        if uncertainty > 5:
            response += f" (±{uncertainty:.0f})"
        
        response += f"\n📈 **Expected Category**: {category}\n"
        response += f"💡 **Health Advice**: {health_message}\n\n"
        
        response += f"**Prediction factors:**\n"
        response += f"🌡️ Season: {'Winter (High pollution)' if target_date.month in [11,12,1,2] else 'Monsoon (Lower pollution)' if target_date.month in [7,8,9] else 'Summer/Spring'}\n"
        response += f"📅 Day: {target_date.strftime('%A')}\n"
        response += f"💨 Current Wind: {data.get('wind_speed', 'N/A')} m/s\n"
        response += f"🔬 Current PM2.5: {data.get('pm25', 'N/A')}"

        # Add confidence note
        if days_ahead > 3:
            response += f"\n\n⚠️ **Note**: Predictions beyond 3 days have higher uncertainty."
        
        # Add recommendation
        response += f"\n\n{self.get_activity_recommendation(predicted_aqi, date_str)}"
        
        return response
    
    def get_contextual_advice(self, aqi, category):
        """Get contextual advice based on AQI"""
        if aqi <= 50:
            return "✅ Perfect day for outdoor activities!"
        elif aqi <= 100:
            return "👍 Generally acceptable for most outdoor activities."
        elif aqi <= 150:
            return "⚠️ Sensitive individuals should consider limiting prolonged outdoor activities."
        elif aqi <= 200:
            return "🚫 Avoid prolonged outdoor activities. Wear a mask if you must go out."
        elif aqi <= 300:
            return "⛔ Stay indoors. Use air purifiers. Wear N95 masks if going out is essential."
        else:
            return "🆘 Health emergency! Avoid going outside. Keep all windows closed."
    
    def get_activity_recommendation(self, aqi, date_str):
        """Get activity recommendations"""
        if aqi <= 50:
            return f"✅ **Recommendation for {date_str}**: Great day for jogging, cycling, or outdoor sports!"
        elif aqi <= 100:
            return f"👍 **Recommendation for {date_str}**: You can exercise outdoors, but take breaks if needed."
        elif aqi <= 150:
            return f"⚠️ **Recommendation for {date_str}**: Consider indoor exercises. If going out, avoid rush hour traffic."
        elif aqi <= 200:
            return f"🚫 **Recommendation for {date_str}**: Stay indoors. Opt for indoor workouts."
        else:
            return f"⛔ **Recommendation for {date_str}**: Minimize outdoor exposure. Work from home if possible."
    
    def get_comparison_response(self, message):
        """Compare current vs predicted AQI"""
        current_data = self.data_fetcher.get_combined_data()
        
        if not current_data:
            return "Sorry, I couldn't fetch comparison data."
        
        current_aqi = current_data.get('aqi', 0)
        predicted_aqi = self.predictor.predict(current_data)
        
        diff = predicted_aqi - current_aqi
        percent_change = (diff / current_aqi) * 100 if current_aqi > 0 else 0
        
        response = f"📊 **AQI Comparison**\n\n"
        response += f"**Today**: {current_aqi:.0f}\n"
        response += f"**Tomorrow (Predicted)**: {predicted_aqi:.0f}\n\n"
        
        if abs(diff) < 10:
            response += f"📈 **Trend**: Stable (change of {diff:.0f})\n"
        elif diff > 0:
            response += f"📈 **Trend**: Worsening (↑ {diff:.0f} or +{percent_change:.1f}%)\n"
        else:
            response += f"📉 **Trend**: Improving (↓ {abs(diff):.0f} or {percent_change:.1f}%)\n"
        
        return response
    
    def get_trend_response(self):
        """Get AQI trend information"""
        return """📊 **Delhi AQI Trends**

**Seasonal Patterns:**
🥶 **Winter (Nov-Feb)**: Highest AQI (150-400)
- Stubble burning, low wind, fog trapping

☀️ **Summer (Mar-Jun)**: Moderate AQI (80-200)
- Dust storms, heat

🌧️ **Monsoon (Jul-Sep)**: Best AQI (50-150)
- Rain washes pollutants

**Daily Patterns:**
- Worst: Early morning & evening (traffic hours)
- Best: Afternoon (wind dispersal)

Want a specific date prediction? Just ask!"""
    
    def get_smart_response(self, message):
        """Handle miscellaneous queries intelligently"""
        message_lower = message.lower()
        
        # Activity-based queries
        if any(word in message_lower for word in ['run', 'jog', 'exercise', 'workout', 'cycling']):
            data = self.data_fetcher.get_combined_data()
            if data:
                aqi = data.get('aqi', 0)
                if aqi <= 100:
                    return f"🏃 Current AQI is {aqi:.0f}. Safe for outdoor exercise! Enjoy your workout!"
                elif aqi <= 150:
                    return f"⚠️ Current AQI is {aqi:.0f}. Consider indoor exercise or shorter outdoor sessions."
                else:
                    return f"🚫 Current AQI is {aqi:.0f}. Recommend indoor exercise only."
        
        # Safety queries
        if any(word in message_lower for word in ['safe', 'okay', 'fine', 'good to go']):
            data = self.data_fetcher.get_combined_data()
            if data:
                aqi = data.get('aqi', 0)
                category, _ = self.predictor.get_aqi_category(aqi)
                return f"Current AQI: {aqi:.0f} ({category})\n\n{self.get_contextual_advice(aqi, category)}"
        
        # Default
        return """I'm not sure I understood that. Try asking:
• "What's the AQI tomorrow?"
• "Predict AQI for Friday"
• "Is it safe to exercise today?"
• "What will the air quality be next week?"

Type 'help' to see all I can do!"""
    
    def get_graph_response(self):
        """Generate 7-day past and future AQI graph"""
        data = self.data_fetcher.get_combined_data()
        
        if not data:
            return "Sorry, I couldn't fetch data for the graph. Please try again later."
        
        # Get past 7 days
        past_data = self.predictor.get_past_n_days(7)
        
        # Get future 7 days predictions
        future_data = self.predictor.predict_next_n_days(data, 7)
        
        # Generate graph data for frontend
        graph_data = {
            'past': past_data,
            'future': future_data
        }
        
        # Create text response
        response = "📊 **14-Day AQI Trend for Delhi**\n\n"
        
        response += "**Past 7 Days:**\n"
        if past_data:
            for entry in past_data:
                category, _ = self.predictor.get_aqi_category(entry['aqi'])
                emoji = self.get_aqi_emoji(entry['aqi'])
                response += f"{emoji} {entry['day_name'][:3]} ({entry['date']}): {entry['aqi']:.0f} - {category}\n"
        else:
            response += "Historical data not available\n"
        
        response += f"\n📍 **Today**: {data.get('aqi', 'N/A')}\n\n"
        
        response += "**Next 7 Days (Predicted):**\n"
        for entry in future_data:
            category, _ = self.predictor.get_aqi_category(entry['aqi'])
            emoji = self.get_aqi_emoji(entry['aqi'])
            response += f"{emoji} {entry['day_name'][:3]} ({entry['date']}): {entry['aqi']:.0f} - {category}\n"
        
        response += "\n💡 **Tip**: Type 'predict for [date]' for specific day details!"
        
        # Return both text and graph data
        return {
            'text': response,
            'graph_data': graph_data
        }
    
    def get_aqi_emoji(self, aqi):
        """Get emoji based on AQI value"""
        if aqi <= 50:
            return "🟢"
        elif aqi <= 100:
            return "🟡"
        elif aqi <= 150:
            return "🟠"
        elif aqi <= 200:
            return "🔴"
        elif aqi <= 300:
            return "🟣"
        else:
            return "🟤"
    
    def parse_query(self, query):
        """Parse user query and return appropriate response"""
        query = query.lower().strip()
        
        # Check for help
        if query in ['help', 'what can you do', 'commands']:
            return self.get_help_message()
        
        # Check for greeting
        if any(word in query for word in ['hello', 'hi', 'hey']):
            return "Hello! I'm your AQI assistant. Ask me about air quality predictions!"
        
        # Parse specific dates (e.g., "17th january", "january 17", "jan 17")
        date_match = self.parse_specific_date(query)
        if date_match:
            try:
                predicted_aqi = self.predictor.predict_for_date(self.current_data, date_match)
                if predicted_aqi:
                    category, health_msg = self.predictor.get_aqi_category(predicted_aqi)
                    date_str = date_match.strftime('%B %d, %Y')
                    day_name = date_match.strftime('%A')
                    
                    return f"""📅 AQI Prediction for {date_str} ({day_name}):

🌡️ Predicted AQI: {predicted_aqi:.1f}
📊 Category: {category}

💡 {health_msg}"""
                else:
                    return "Sorry, I couldn't generate a prediction for that date. Please try again."
            except Exception as e:
                print(f"Error predicting for specific date: {e}")
                return "Sorry, I encountered an error predicting for that date."
        
        # Check for next N days prediction
        if 'next' in query and 'days' in query:
            match = re.search(r'next\s+(\d+)\s+days?', query)
            if match:
                n_days = int(match.group(1))
                return self.get_next_n_days_prediction(n_days)
        
        # Check for prediction queries
        if any(word in query for word in ['predict', 'forecast', 'will be', 'going to be']):
            if 'tomorrow' in query:
                return self.get_tomorrow_prediction()
            elif 'week' in query:
                return self.get_week_prediction()
            elif any(day in query for day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']):
                return self.get_day_prediction(query)
        
        # Check for current AQI
        if any(word in query for word in ['current', 'now', 'today']):
            return self.get_current_aqi()
        
        # Check for tomorrow
        if 'tomorrow' in query:
            return self.get_tomorrow_prediction()
        
        # Check for specific day
        if any(day in query for day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']):
            return self.get_day_prediction(query)
        
        # Check for week prediction
        if 'week' in query or '7 day' in query:
            return self.get_week_prediction()
        
        # Check for safety/exercise queries
        if any(word in query for word in ['safe', 'exercise', 'outdoor', 'go out', 'running', 'jogging']):
            return self.get_safety_advice()
        
        # Check for past data
        if any(word in query for word in ['yesterday', 'past', 'history', 'last week']):
            return self.get_past_data()
        
        # Default response
        return """I'm not sure I understood that. Try asking:
• "What's the AQI tomorrow?"
• "Predict AQI for Friday"
• "What will the AQI be on January 17?"
• "Is it safe to exercise today?"
• "What will the air quality be next week?"

Type 'help' to see all I can do!"""
    
    def parse_specific_date(self, query):
        """Parse specific date from query like '17th january', 'january 17', 'jan 17'"""
        current_year = datetime.now().year
        
        # Month names and abbreviations
        months = {
            'january': 1, 'jan': 1,
            'february': 2, 'feb': 2,
            'march': 3, 'mar': 3,
            'april': 4, 'apr': 4,
            'may': 5,
            'june': 6, 'jun': 6,
            'july': 7, 'jul': 7,
            'august': 8, 'aug': 8,
            'september': 9, 'sep': 9, 'sept': 9,
            'october': 10, 'oct': 10,
            'november': 11, 'nov': 11,
            'december': 12, 'dec': 12
        }
        
        # Pattern 1: "17th january", "17 january"
        pattern1 = r'(\d{1,2})(?:st|nd|rd|th)?\s+(january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)'
        match = re.search(pattern1, query, re.IGNORECASE)
        if match:
            day = int(match.group(1))
            month_name = match.group(2).lower()
            month = months[month_name]
            
            try:
                target_date = datetime(current_year, month, day)
                # If the date is in the past, assume next year
                if target_date < datetime.now():
                    target_date = datetime(current_year + 1, month, day)
                return target_date
            except ValueError:
                return None
        
        # Pattern 2: "january 17", "jan 17"
        pattern2 = r'(january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)\s+(\d{1,2})(?:st|nd|rd|th)?'
        match = re.search(pattern2, query, re.IGNORECASE)
        if match:
            month_name = match.group(1).lower()
            day = int(match.group(2))
            month = months[month_name]
            
            try:
                target_date = datetime(current_year, month, day)
                # If the date is in the past, assume next year
                if target_date < datetime.now():
                    target_date = datetime(current_year + 1, month, day)
                return target_date
            except ValueError:
                return None
        
        # Pattern 3: "on the 17th"
        pattern3 = r'on\s+the\s+(\d{1,2})(?:st|nd|rd|th)?'
        match = re.search(pattern3, query)
        if match:
            day = int(match.group(1))
            current_month = datetime.now().month
            current_day = datetime.now().day
            
            try:
                if day > current_day:
                    target_date = datetime(current_year, current_month, day)
                else:
                    # Next month
                    next_month = current_month + 1 if current_month < 12 else 1
                    next_year = current_year if current_month < 12 else current_year + 1
                    target_date = datetime(next_year, next_month, day)
                return target_date
            except ValueError:
                return None
        
        return None