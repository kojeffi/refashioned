import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
import joblib

# Load the dataset
data = pd.read_csv('Year_10_11.csv')

# Preprocess the data
# Compute features for each customer
data['TotalPrice'] = data['Quantity'] * data['Price']
customer_data = data.groupby('Customer ID').agg({
    'TotalPrice': 'sum',
    'Quantity': 'sum',
    'InvoiceDate': lambda x: (pd.Timestamp.now() - pd.to_datetime(x).max()).days  # Days since last purchase
}).reset_index()

# Define the target variable as TotalPrice (for demonstration; adjust according to your use case)
customer_data['CLV'] = customer_data['TotalPrice']

# Features and target
X = customer_data[['TotalPrice', 'Quantity', 'InvoiceDate']]
y = customer_data['CLV']

# Split the data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train the model
model = LinearRegression()
model.fit(X_train, y_train)

# Save the model
joblib.dump(model, 'clv_model.pkl')
