from foundry_local_sdk import Configuration, FoundryLocalManager


FoundryLocalManager.initialize(
    Configuration(app_name="citizen-service-local")
)

manager = FoundryLocalManager.instance

model_alias = "phi-4-mini-reasoning"
model = manager.catalog.get_model(model_alias)

if model is None:
    available_models = ", ".join(
        item.alias
        for item in manager.catalog.list_models()
    )
    raise RuntimeError(
        f"Model '{model_alias}' is not available. "
        f"Available models: {available_models}"
    )

model.download(
    lambda progress: print(
        f"\rDownloading: {progress:.0%}",
        end=""
    )
)

print()

model.load()

client = model.get_chat_client()

response = client.complete_chat(
    [
        {
            "role": "user",
            "content": "Explain citizen service requests in one sentence."
        }
    ]
)

print(response)

model.unload()