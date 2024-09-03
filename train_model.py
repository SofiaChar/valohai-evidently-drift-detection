import json

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
import joblib

# Load the preprocessed data
housing_data = pd.read_csv("/valohai/inputs/dataset/housing_data.csv")

# Drop any unnamed columns
housing_data = housing_data.loc[:, ~housing_data.columns.str.contains('^Unnamed')]

# Split the data for training
X = housing_data.drop(columns=['target', 'prediction'])
y = housing_data['target']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train a RandomForest model
model = RandomForestRegressor(random_state=42)
model.fit(X_train, y_train)

# Save the trained model
joblib.dump(model, "/valohai/outputs/random_forest_model.joblib")

metadata = {"valohai.alias": "california_housing_model"}
metadata_path = '/valohai/outputs/random_forest_model.joblib.metadata.json'
with open(metadata_path, 'w') as outfile:
    json.dump(metadata, outfile)
