import pandas as pd
import valohai
import json
import joblib
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset, TargetDriftPreset, DataQualityPreset, RegressionPreset
from evidently.metrics import ColumnSummaryMetric, ColumnQuantileMetric, ColumnDriftMetric
from evidently.metrics.base_metric import generate_column_metrics

# Load the preprocessed data
housing_data = pd.read_csv("/valohai/inputs/ref_dataset/housing_data.csv")
housing_data_current = pd.read_csv("/valohai/inputs/cur_dataset/evidently_data_with_drift.csv")

# Drop any unnamed columns
housing_data = housing_data.loc[:, ~housing_data.columns.str.contains('^Unnamed')]
housing_data_current = housing_data_current.loc[:, ~housing_data_current.columns.str.contains('^Unnamed')]

# Load the trained model
model = joblib.load("/valohai/inputs/model/random_forest_model.joblib")

# Make predictions
housing_data['prediction'] = model.predict(housing_data.drop(columns=['target', 'prediction']))
housing_data_current['prediction'] = model.predict(housing_data_current.drop(columns=['target']))

# Split the data into reference and current datasets
reference = housing_data.sample(n=5000, replace=False)
current = housing_data_current.sample(n=5000, replace=False)

# Generate a Data Drift Report
report = Report(metrics=[
    DataDriftPreset(),
])
report.run(reference_data=reference, current_data=current)
report.save("/valohai/outputs/data_drift_report.json")

# Generate Column-Specific Reports
report = Report(metrics=[
    ColumnSummaryMetric(column_name='AveRooms'),
    ColumnQuantileMetric(column_name='AveRooms', quantile=0.25),
    ColumnDriftMetric(column_name='AveRooms'),
])
report.run(reference_data=reference, current_data=current)
report.save("/valohai/outputs/column_specific_report.json")

# Generate Custom Column Metrics
report = Report(metrics=[
    generate_column_metrics(ColumnQuantileMetric, parameters={'quantile': 0.25}, columns=['AveRooms', 'AveBedrms']),
])
report.run(reference_data=reference, current_data=current)
report.save("/valohai/outputs/custom_column_metrics_report.json")

# Combining Multiple Metrics in a Report
report = Report(metrics=[
    ColumnSummaryMetric(column_name='AveRooms'),
    generate_column_metrics(ColumnQuantileMetric, parameters={'quantile': 0.25}, columns='num'),
    DataDriftPreset()
])
report.run(reference_data=reference, current_data=current)
report.save("/valohai/outputs/combined_metrics_report.json")

# Save the final report
report_dict = report.as_dict()
report_json = report.json()
with open("/valohai/outputs/final_report.json", "w") as file:
    file.write(report_json)

# Load JSON data
with open('/valohai/outputs/data_drift_report.json', 'r') as file:
    data = json.load(file)

# Extract Drift Status
def extract_drift_status(data):
    drift_status = {}
    for section in data['suite']['metric_results']:
        if 'dataset_drift' in section and section['dataset_drift']:
            drift_status['data_drift'] = section['dataset_drift']
        if 'drift_by_columns' in section:
            for column, metrics in section['drift_by_columns'].items():
                drift_status[column] = metrics['drift_detected']
    return drift_status

drift_status = extract_drift_status(data)

true_metrics = [key for key, value in drift_status.items() if value]

# Check if there are any True values and print results
if true_metrics:
    print("Drift detected in the dataset.")
    valohai.set_status_detail("Drift Detected in the dataset")
    print(json.dumps({'drift': 1}))
    for metric in true_metrics:
        print(f"Metric '{metric}' has data drift detected")
else:
    print("No drift detected in the dataset.")
    valohai.set_status_detail("No drift detected in the dataset")

# Save dataset uri as metadata to pass it to next node of the pipeline
with open('/valohai/config/inputs.json') as json_file:
    vh_inputs_config = json.load(json_file)

file_info = vh_inputs_config.get('cur_dataset', {}).get('files', [])[0]
data_url = file_info.get('storage_uri', file_info.get('uri'))

# Print json.dumps - to save the metadata
if data_url:
    print(json.dumps({'dataset_path': data_url}))
