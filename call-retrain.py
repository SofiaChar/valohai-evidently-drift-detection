import requests
import valohai
import os

auth_token = os.environ.get("VALOHAI_API_TOKEN")
dataset_path = valohai.parameters('dataset_path').value

resp = requests.request(
    url="https://app.valohai.com/api/v0/pipelines/",
    method="POST",
    headers={"Authorization": f"Token {auth_token}"},
    json={
        "edges": [
            {
                "source_node": "preprocess-node",
                "source_key": "*.csv",
                "source_type": "output",
                "target_node": "train-model-node",
                "target_type": "input",
                "target_key": "dataset"
            }
        ],
        "nodes": [
            {
                "name": "preprocess-node",
                "type": "execution",
                "on_error": "stop-all",
                "template": {
                    "environment": "0167d05d-a1d7-cc02-8256-6455a6ecfa56",
                    "commit": "main",
                    "step": "preprocess",
                    "image": "python:3.9",
                    "command": "pip install evidently==0.4.16 pandas==2.2.1 scikit-learn==1.4.1.post1 valohai\npython preprocess.py",
                    "inputs": {
                        "dataset": [dataset_path]
                    },
                    "parameters": {},
                    "runtime_config": {},
                    "inherit_environment_variables": True,
                    "environment_variable_groups": [],
                    "tags": [],
                    "time_limit": 0,
                    "environment_variables": {},
                    "allow_reuse": False
                }
            },
            {
                "name": "train-model-node",
                "type": "execution",
                "on_error": "stop-all",
                "template": {
                    "environment": "0167d05d-a1d7-cc02-8256-6455a6ecfa56",
                    "commit": "main",
                    "step": "train_model",
                    "image": "python:3.9",
                    "command": "pip install evidently==0.4.16 pandas==2.2.1 scikit-learn==1.4.1.post1\npython train_model.py",
                    "inputs": {
                        "dataset": [
                            "datum://california_housing_dataset"
                        ]
                    },
                    "parameters": {},
                    "runtime_config": {},
                    "inherit_environment_variables": True,
                    "environment_variable_groups": [],
                    "tags": [],
                    "time_limit": 0,
                    "environment_variables": {},
                    "allow_reuse": False
                }
            }
        ],
        "project": "0190fe5c-ca46-bf10-880d-d92127f69fd2",
        "tags": [],
        "parameters": {},
        "title": "train-pipeline-triggered-because-drift-detected"
    },
)
if resp.status_code == 400:
    raise RuntimeError(resp.json())
resp.raise_for_status()
data = resp.json()
