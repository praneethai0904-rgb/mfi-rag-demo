import os
import json
import requests

RAW_DIR = "data/raw"
PROCESSED_DIR = "data/processed"
UNSTRUCTURED_URL = "http://localhost:8000/general/v0/general"

os.makedirs(PROCESSED_DIR, exist_ok=True)

# Look for files in data/raw
files_to_parse = [f for f in os.listdir(RAW_DIR) if f.endswith(".pdf")]

if not files_to_parse:
    print(f"No PDF files found in '{RAW_DIR}'. Please drop some PDFs there first!")
else:
    for filename in files_to_parse:
        file_path = os.path.join(RAW_DIR, filename)
        print(f"Sending {filename} to local Unstructured API...")
        
        with open(file_path, "rb") as f:
            files = {"files": (filename, f, "application/pdf")}
            data = {"strategy": "fast"} 
            
            response = requests.post(UNSTRUCTURED_URL, files=files, data=data)
            
        if response.status_code == 200:
            output_elements = response.json()
            output_filename = filename.replace(".pdf", ".json")
            output_path = os.path.join(PROCESSED_DIR, output_filename)
            
            with open(output_path, "w", encoding="utf-8") as out_f:
                json.dump(output_elements, out_f, indent=2, ensure_ascii=False)
            print(f"✅ Successfully saved parsed data to: {output_path}\n")
        else:
            print(f"❌ Failed to parse {filename}: {response.text}\n")