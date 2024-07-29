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
housing_data_current = pd.read_csv("/valohai/inputs/cur_dataset/evidently_current_data_with_drift.csv")

# Load the trained model
model = joblib.load("/valohai/inputs/model/random_forest_model.joblib")

# Make predictions
housing_data['prediction'] = model.predict(housing_data.drop(columns=['target', 'prediction']))
housing_data_current['prediction'] = model.predict(housing_data_current.drop(columns=['target', 'prediction']))

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
print(drift_status)

# Check for dataset drift
if 'data_drift' in drift_status and drift_status['data_drift']:
    print("Drift detected in the dataset.")
    valohai.set_status_detail("Drift Detected in the dataset")
else:
    print("No drift detected in the dataset.")
    valohai.set_status_detail("No drift detected in the dataset")
