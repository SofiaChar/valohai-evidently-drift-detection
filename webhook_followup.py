
import valohai
valohai.prepare(
    step="Webhook Followup",
)

prompt = valohai.parameters("prompt").value
print("Received prompt:", prompt)
print("---")
print("This is just a demonstration to pass values around in a pipeline, so not doing anything useful with it.")