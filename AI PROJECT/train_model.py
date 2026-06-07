import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import mean_absolute_error, r2_score
import joblib

# Load dataset
df = pd.read_csv("d:/AI PROJECT/pakistan_weather_2000_2024.csv")
df['date'] = pd.to_datetime(df['date'])

# Drop visibility since it's 100% missing
df = df.drop(columns=['visibility'])

# Create binary rain target: 1 if prcp > 0, else 0
df['is_rain'] = (df['prcp'] > 0).astype(int)

# Sort by city and date
df = df.sort_values(by=['city', 'date']).reset_index(drop=True)

# Encode city
city_encoder = LabelEncoder()
df['city_encoded'] = city_encoder.fit_transform(df['city'])

# Define variables we want to use for lag features
lag_vars = ['tavg', 'tmin', 'tmax', 'humidity', 'wspd', 'prcp', 'pressure', 'cloud_cover', 'is_rain']
window_size = 7
forecast_horizon = 3

# Vectorized lag features
lagged_dfs = [df]
for d in range(window_size):
    if d > 0:
        lagged_df = df.groupby('city')[lag_vars].shift(d)
        lagged_df.columns = [f'{var}_lag_{d}' for var in lag_vars]
        lagged_dfs.append(lagged_df)
    else:
        lagged_df = df[lag_vars].copy()
        lagged_df.columns = [f'{var}_lag_0' for var in lag_vars]
        lagged_dfs.append(lagged_df)

# Vectorized target leads
target_vars = ['tavg', 'humidity', 'wspd', 'is_rain', 'cloud_cover']
for h in range(1, forecast_horizon + 1):
    lead_df = df.groupby('city')[target_vars].shift(-h)
    lead_df.columns = [f'{var}_lead_{h}' for var in target_vars]
    lagged_dfs.append(lead_df)

# Concatenate all features and targets
df_feat = pd.concat(lagged_dfs, axis=1)

# Add other non-lag features
df_feat['month'] = df['date'].dt.month
df_feat['day'] = df['date'].dt.day
df_feat['dayofweek'] = df['date'].dt.dayofweek

# Drop rows with NaN (due to lags and leads at start/end of series)
df_feat = df_feat.dropna().reset_index(drop=True)

# Separate features X and targets y
feature_cols = ['city_encoded', 'latitude', 'longitude', 'elevation', 'month', 'day', 'dayofweek']
for d in range(window_size):
    for var in lag_vars:
        feature_cols.append(f'{var}_lag_{d}')

target_cols = []
for h in range(1, forecast_horizon + 1):
    for var in target_vars:
        target_cols.append(f'{var}_lead_{h}')

X = df_feat[feature_cols]
y = df_feat[target_cols]

print("X shape:", X.shape)
print("y shape:", y.shape)

# Train-test split (80-20 random split)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Scale features
scaler = StandardScaler()
num_cols = [col for col in X.columns if col != 'city_encoded']
X_train_scaled = X_train.copy()
X_test_scaled = X_test.copy()

X_train_scaled[num_cols] = scaler.fit_transform(X_train[num_cols])
X_test_scaled[num_cols] = scaler.transform(X_test[num_cols])

# Train Random Forest Regressor
print("\nTraining Random Forest Regressor...")
model = RandomForestRegressor(n_estimators=100, max_depth=12, random_state=42, n_jobs=-1)
model.fit(X_train_scaled, y_train)

# Evaluate model
y_pred = model.predict(X_test_scaled)
y_pred = pd.DataFrame(y_pred, columns=y.columns)

print("\nModel Evaluation (MAE):")
for col in y.columns:
    mae = mean_absolute_error(y_test[col], y_pred[col])
    r2 = r2_score(y_test[col], y_pred[col])
    print(f"{col:<20} | MAE: {mae:.3f} | R2: {r2:.3f}")

# Save artifacts
joblib.dump(model, 'd:/AI PROJECT/weather_model.joblib')
joblib.dump(scaler, 'd:/AI PROJECT/scaler.joblib')
joblib.dump(city_encoder, 'd:/AI PROJECT/city_encoder.joblib')
print("\nModel and preprocessing objects saved successfully!")
