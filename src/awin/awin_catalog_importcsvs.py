import os
import csv
import psycopg2
from dotenv import load_dotenv
from datetime import datetime
import time

# Load environment variables
load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_DATABASE = os.getenv("DB_DATABASE")
BATCH_SIZE = int(os.getenv("BATCH_SIZE", 5000))
AWIN_PARTNER_ID = os.getenv("AWIN_PARTNER_ID")

# CSV files are now in /data/awin/csv
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CSV_DIR = os.path.join(PROJECT_ROOT, 'data', 'awin', 'csv')
LOG_DIR = os.path.join(PROJECT_ROOT, 'data', 'awin', 'log')
os.makedirs(LOG_DIR, exist_ok=True)  # Ensure log directory exists
LOG_FILENAME = datetime.now().strftime("%d%m%Y_%H%M%S") + ".log"
LOG_PATH = os.path.join(LOG_DIR, LOG_FILENAME)

TABLE_DDL = """
DROP TABLE IF EXISTS awin_catalog_import_temp;
CREATE TABLE awin_catalog_import_temp (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    imported BOOLEAN DEFAULT FALSE,
    partner_id INTEGER,
    aw_deep_link TEXT,
    product_name TEXT,
    aw_product_id TEXT,
    merchant_product_id TEXT,
    merchant_image_url TEXT,
    description TEXT,
    merchant_category TEXT,
    search_price TEXT,
    merchant_name TEXT,
    merchant_id INTEGER,
    category_name TEXT,
    category_id TEXT,
    aw_image_url TEXT,
    currency TEXT,
    store_price TEXT,
    delivery_cost TEXT,
    merchant_deep_link TEXT,
    "language" TEXT,
    last_updated TEXT,
    display_price TEXT,
    data_feed_id TEXT,
    brand_name TEXT,
    brand_id TEXT,
    colour TEXT,
    product_short_description TEXT,
    specifications TEXT,
    "condition" TEXT,
    product_model TEXT,
    model_number TEXT,
    dimensions TEXT,
    keywords TEXT,
    promotional_text TEXT,
    product_type TEXT,
    commission_group TEXT,
    merchant_product_category_path TEXT,
    merchant_product_second_category TEXT,
    merchant_product_third_category TEXT,
    rrp_price TEXT,
    saving TEXT,
    savings_percent TEXT,
    base_price TEXT,
    base_price_amount TEXT,
    base_price_text TEXT,
    product_price_old TEXT,
    delivery_restrictions TEXT,
    delivery_weight TEXT,
    warranty TEXT,
    terms_of_contract TEXT,
    delivery_time TEXT,
    in_stock BOOLEAN,
    stock_quantity TEXT,
    valid_from TEXT,
    valid_to TEXT,
    is_for_sale BOOLEAN,
    web_offer BOOLEAN,
    pre_order BOOLEAN,
    stock_status TEXT,
    size_stock_status TEXT,
    size_stock_amount TEXT,
    merchant_thumb_url TEXT,
    large_image TEXT,
    alternate_image TEXT,
    aw_thumb_url TEXT,
    alternate_image_two TEXT,
    alternate_image_three TEXT,
    alternate_image_four TEXT,
    reviews TEXT,
    average_rating TEXT,
    rating TEXT,
    number_available TEXT,
    custom_1 TEXT,
    custom_2 TEXT,
    custom_3 TEXT,
    custom_4 TEXT,
    custom_5 TEXT,
    custom_6 TEXT,
    custom_7 TEXT,
    custom_8 TEXT,
    custom_9 TEXT,
    ean TEXT,
    isbn TEXT,
    upc TEXT,
    mpn TEXT,
    parent_product_id TEXT,
    product_gtin TEXT,
    basket_link TEXT,
    fashion_suitable_for TEXT,
    fashion_category TEXT,
    fashion_size TEXT,
    fashion_material TEXT,
    fashion_pattern TEXT,
    fashion_swatch TEXT
);

-- Índices para acelerar consultas frequentes
CREATE INDEX idx_awin_imported ON awin_catalog_import_temp(imported);
CREATE INDEX idx_awin_partner_id ON awin_catalog_import_temp(partner_id);
CREATE INDEX idx_awin_merchant_id ON awin_catalog_import_temp(merchant_id);
CREATE INDEX idx_awin_merchant_product_id ON awin_catalog_import_temp(merchant_product_id);
CREATE INDEX idx_awin_aw_product_id ON awin_catalog_import_temp(aw_product_id);
CREATE INDEX idx_awin_last_updated ON awin_catalog_import_temp(last_updated);
"""

def log(msg, icon="ℹ️"):
    log_line = f"{datetime.now().strftime('%d/%m/%Y %H:%M:%S')} {icon} {msg}\n"
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(log_line)
    print(log_line, end="")

def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        dbname=DB_DATABASE
    )

def recreate_awin_catalog_import_temp(conn):
    with conn.cursor() as cur:
        cur.execute(TABLE_DDL)
    conn.commit()
    log("Table awin_catalog_import_temp dropped and recreated.", icon="🗑️")

def process_csv_file(filepath, conn, batch_size):
    start = time.time()
    log(f"Starting processing file: {os.path.basename(filepath)}", icon="📄")
    with open(filepath, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        header = next(reader)
        header = [col.replace(":", "_").lower() for col in header]
        # Ensure partner_id is the first column
        if "partner_id" not in header:
            header = ["partner_id"] + header
        batch = []
        total = 0
        for row in reader:
            # Insert AWIN_PARTNER_ID as the first value if not present
            if "partner_id" not in header or len(row) == len(header) - 1:
                row = [AWIN_PARTNER_ID] + row
            batch.append(row)
            if len(batch) >= batch_size:
                copy_batch(conn, header, batch)
                total += len(batch)
                batch = []
        if batch:
            copy_batch(conn, header, batch)
            total += len(batch)
    elapsed = time.time() - start
    log(f"File {os.path.basename(filepath)} processed: {total} records in {elapsed:.2f} seconds.", icon="✅")

def copy_batch(conn, header, batch):
    from io import StringIO
    with conn.cursor() as cur:
        f = StringIO()
        writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
        writer.writerows(batch)
        f.seek(0)
        columns = ','.join([f'"{col}"' for col in header])
        cur.copy_expert(
            sql=f"COPY awin_catalog_import_temp ({columns}) FROM STDIN WITH CSV",
            file=f
        )
    conn.commit()

def main():
    start_total = time.time()
    log("Process started.", icon="🚀")
    files = [f for f in os.listdir(CSV_DIR) if f.endswith('.csv')]
    log(f"{len(files)} CSV files found to process.", icon="📦")
    conn = get_db_connection()
    try:
        recreate_awin_catalog_import_temp(conn)
        for idx, filename in enumerate(files, 1):
            filepath = os.path.join(CSV_DIR, filename)
            log(f"({idx}/{len(files)}) Processing file: {filename}", icon="🔄")
            process_csv_file(filepath, conn, BATCH_SIZE)
    finally:
        conn.close()
    elapsed_total = time.time() - start_total
    hours = int(elapsed_total // 3600)
    minutes = int((elapsed_total % 3600) // 60)
    log(f"Process finished. Total time: {hours}h {minutes}min.", icon="🏁")

if __name__ == "__main__":
    main()

