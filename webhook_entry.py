import json
import valohai

from urllib.parse import parse_qs

valohai.prepare(
    step="Webhook Entry",
)

with open(valohai.inputs('webhook-payload').path()) as f:
    post_parameters = {k: v[0] for k, v in parse_qs(f.read()).items()}

print("Received these parameters from the webhook:")
for k, v in post_parameters.items():
    print(f"{k}: {v}")
if "prompt" in post_parameters:
    # Submit metadata
    print(json.dumps({'parsed_prompt': post_parameters['prompt']}))