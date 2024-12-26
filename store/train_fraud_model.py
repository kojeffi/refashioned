import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import joblib

# Load the dataset
data_path = ''  # Replace with your dataset path
df = pd.read_csv(data_path)

# Define features and target
features = ['Time', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6', 'V7', 'V8', 'V9', 'V10', 'V11', 'V12', 'V13', 'V14', 'V15', 'V16', 'V17', 'V18', 'V19', 'V20', 'V21', 'V22', 'V23', 'V24', 'V25', 'V26', 'V27', 'V28', 'Amount']
X = df[features]
y = df['Class']  # Target variable

# Preprocess the data
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Initialize and train the Isolation Forest model
isolation_forest = IsolationForest(contamination=0.01)
isolation_forest.fit(X_scaled)

# Save the model and scaler
joblib.dump(isolation_forest, 'isolation_forest_model.pkl')
joblib.dump(scaler, 'scaler.pkl')

print("Model and scaler saved successfully.")
