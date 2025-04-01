from google.cloud import aiplatform
from google.api_core.exceptions import GoogleAPICallError, NotFound

def list_models(project_id, location):
    try:
        client = aiplatform.gapic.ModelServiceClient()
        parent = f"projects/{project_id}/locations/{location}"
        
        response = client.list_models(parent=parent)
        models_found = False
        for model in response:
            models_found = True
            print(f"Model Name: {model.name}")
            print(f"  Supported Methods: {model.supported_deployment_resources_types}")
            print(f"  Display Name: {model.display_name}")
            print(f"  Description: {model.description}\n")
        
        if not models_found:
            print("No models found in the specified project and location.")
    except NotFound:
        print("Error: The specified project or location was not found.")
    except GoogleAPICallError as e:
        print(f"API call error: {e}")

# Replace with your project ID and location
list_models("gen-lang-client-0610396495", "	asia-south1")
