import requests
import os
import json

# Replace with your Docker container's IP/Port
# Usually http://localhost:8000/general/v0/general
UNSTRUCTURED_API_URL = "http://localhost:8000/general/v0/general"

def convert_pdf_to_json(pdf_path, output_json_path):
    with open(pdf_path, 'rb') as f:
        files = {'files': (os.path.basename(pdf_path), f, 'application/pdf')}
        # Send to your Docker container
        response = requests.post(UNSTRUCTURED_API_URL, files=files, data={"strategy": "fast"})
    
    if response.status_code == 200:
        elements = response.json()
        # Save the output to your desired JSON path
        with open(output_json_path, 'w') as f:
            json.dump(elements, f, indent=2)
        print(f"✅ Successfully converted via Docker: {output_json_path}")
    else:
        raise Exception(f"Docker API Error: {response.text}")