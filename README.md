**🌦️ 3-Day Weather Forecasting System (Pakistan)**

A machine learning-powered Streamlit web application that predicts the next 3 days weather forecast for major cities in Pakistan using historical weather data (2000–2024).

**🚀 Project Overview**

This project uses time-series machine learning models to analyze historical weather patterns and forecast:

🌡️ Temperature
💧 Humidity
🌬️ Wind Speed
🌧️ Rainfall probability

The system provides an interactive Streamlit dashboard where users can select a city and instantly get a 3-day weather prediction.

**🎯 Features**
📍 City-wise weather forecasting (Pakistan)
📊 3-day weather prediction using ML models
📈 Visual charts for temperature, humidity, and rainfall
🧠 Supports time-series forecasting using lag features
⚡ Fast predictions via pre-trained model
🎨 Clean and interactive Streamlit UI
☁️ Real-world dataset (2000–2024 weather history)
🧠 Machine Learning Approach

**🔹 Techniques Used:**
Lag features (t-1, t-2, t-3 days)
Feature scaling (StandardScaler / MinMaxScaler)
Time-series forecasting approach
🔹 Possible Models:
Random Forest Regressor

**⚙️ Installation & Setup**
1️⃣ Clone the Repository
git clone https://github.com/shayan-mir002/weather-prediction-model.git
cd AI PROJECT
2️⃣ Install Dependencies
pip install -r requirements.txt

If requirements.txt is not available:

pip install streamlit pandas numpy scikit-learn matplotlib
3️⃣ Run the Streamlit App
streamlit run app.py

**🖥️ How It Works**
User selects a city from sidebar
System loads historical weather patterns
ML model processes lag-based features
Forecast is generated for next 3 days
Results displayed with charts and metrics


