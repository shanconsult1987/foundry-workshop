from azure.identity import DefaultAzureCredential


credential = DefaultAzureCredential()

token = credential.get_token(
    "https://ai.azure.com/.default"
)

print("Azure authentication successful.")
print("Token acquired successfully.")