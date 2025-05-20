import os
import csv
import gzip
import shutil
import requests
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Directories (now relative to the project root, not src)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LISTS_DIR = os.path.join(PROJECT_ROOT, 'data', 'awin', 'lists')
INPUTS_DIR = os.path.join(PROJECT_ROOT, 'data', 'awin')

os.makedirs(LISTS_DIR, exist_ok=True)
os.makedirs(INPUTS_DIR, exist_ok=True)

# Configurations
AWIN_API_KEY = os.getenv("AWIN_API_KEY")
AWIN_PUBLISHER_ID = os.getenv("AWIN_PUBLISHER_ID")
AWIN_LIST_URL = f"https://ui.awin.com/productdata-darwin-download/publisher/{AWIN_PUBLISHER_ID}/{AWIN_API_KEY}/1/feedList"
TODAY = datetime.now().strftime("%d%m%Y")
LIST_FILENAME = f"{TODAY}-Awin_List.csv"
LIST_PATH = os.path.join(LISTS_DIR, LIST_FILENAME)
LOG_PATH = os.path.join(LISTS_DIR, f"{TODAY}-execution.log")

def log(msg, level="INFO"):
    now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    line = f"[{level}] {msg} ({now})"
    print(line)
    with open(LOG_PATH, "a") as f:
        f.write(line + "\n")

def download_and_extract(url, dest_csv):
    gz_path = dest_csv + ".gz"
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(gz_path, "wb") as f:
            shutil.copyfileobj(r.raw, f)
    with gzip.open(gz_path, 'rb') as f_in, open(dest_csv, 'wb') as f_out:
        shutil.copyfileobj(f_in, f_out)
    os.remove(gz_path)

def filter_active_stores(csv_path):
    active_stores = []
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row.get("Membership Status", "").strip().lower() == "active":
                active_stores.append(row)
    return active_stores

def download_store_catalogs(stores):
    for store in stores:
        advertiser_id = store["Advertiser ID"].strip()
        advertiser_name = store["Advertiser Name"].strip().replace(" ", "_")
        url = store["URL"].strip()
        file_name = f"{TODAY}-{advertiser_id}-{advertiser_name}.csv"
        dest_csv = os.path.join(INPUTS_DIR, file_name)
        try:
            log(f"Downloading catalog: {advertiser_id} - {advertiser_name}")
            download_and_extract(url, dest_csv)
            log(f"Catalog saved at: {dest_csv}")
        except Exception as e:
            log(f"Error downloading catalog {advertiser_id} - {advertiser_name}: {e}", level="ERROR")

def format_time(seconds):
    minutes = int(seconds // 60)
    hours = int(minutes // 60)
    minutes = minutes % 60
    if hours > 0:
        return f"{hours}h {minutes}min"
    else:
        return f"{minutes}min"

def main():
    start = datetime.now()
    log("Starting AWIN ingestion process")

    # 1. Download and extract main list
    try:
        log("Downloading AWIN main list...")
        download_and_extract(AWIN_LIST_URL, LIST_PATH)
        log(f"Main list file downloaded and extracted: {LIST_PATH}")
    except Exception as e:
        log(f"Error downloading/extracting main list: {e}", level="ERROR")
        return

    # 2. Filter active stores
    active_stores = filter_active_stores(LIST_PATH)
    log(f"Active stores found: {len(active_stores)}")

    # 3. Download catalogs for active stores
    download_store_catalogs(active_stores)

    end = datetime.now()
    total_time = (end - start).total_seconds()
    formatted_time = format_time(total_time)
    log("Process finished")
    log(f"Total execution time: {formatted_time}")

if __name__ == "__main__":
    main()