import json

import pandas as pd
import numpy as np
from sklearn.datasets import fetch_california_housing

# Load the dataset
data = fetch_california_housing(as_frame=True)
housing_data = data.frame

# Rename the target column
housing_data.rename(columns={'MedHouseVal': 'target'}, inplace=True)

# Add a prediction column with some noise
housing_data['prediction'] = housing_data['target'].values + np.random.normal(0, 5, housing_data.shape[0])

# Save the preprocessed data
housing_data.to_csv("/valohai/outputs/housing_data.csv")

metadata = {"valohai.alias": "california_housing_dataset"}
metadata_path = '/valohai/outputs/housing_data.csv.metadata.json'
with open(metadata_path, 'w') as outfile:
    json.dump(metadata, outfile)