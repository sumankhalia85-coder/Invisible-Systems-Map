import os
import requests
import re
import zipfile
import tempfile
import gdelt_ingest

def download_and_ingest_latest():
    url = "http://data.gdeltproject.org/events/"
    print(f"Fetching GDELT index from {url}")
    r = requests.get(url, timeout=30)
    r.raise_for_status()

    # Regex to find the latest .export.CSV.zip (format: YYYYMMDD.export.CSV.zip)
    matches = re.findall(r'href=["\']?(\d{8}\.export\.CSV\.zip)["\']?', r.text, re.IGNORECASE)
    if not matches:
        raise Exception("Could not find any export.CSV.zip files on the index page.")
        
    # Sort backwards to get the latest date
    matches.sort(reverse=True)
    latest_file = matches[0]
    file_url = f"{url}{latest_file}"
    
    print(f"Downloading latest GDELT dataset: {file_url}")
    
    tmp_zip = os.path.join(tempfile.gettempdir(), latest_file)
    r_file = requests.get(file_url, stream=True, timeout=60)
    r_file.raise_for_status()
    
    with open(tmp_zip, 'wb') as f:
        for chunk in r_file.iter_content(chunk_size=8192):
            f.write(chunk)
            
    print(f"Extracting {tmp_zip}")
    # Extract to temp dir
    with zipfile.ZipFile(tmp_zip, 'r') as zip_ref:
        csv_filename = zip_ref.namelist()[0]
        extraction_path = tempfile.gettempdir()
        zip_ref.extractall(extraction_path)
        
    extracted_csv = os.path.join(extraction_path, csv_filename)
    print(f"Executing GDELT ingestion pipeline on {extracted_csv}")
    
    # Run gdelt_ingest
    events = gdelt_ingest.process_gdelt(extracted_csv)
    
    # Cleanup
    try:
        os.remove(tmp_zip)
        os.remove(extracted_csv)
    except:
        pass
        
    print("Update complete.")

if __name__ == "__main__":
    download_and_ingest_latest()
