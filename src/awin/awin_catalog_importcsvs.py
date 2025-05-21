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
DROP TABLE IF EXISTS awin_catalogo_import_temp;
CREATE TABLE public.awin_catalogo_import_temp (
    id serial4 NOT NULL,
    created_at timestamp DEFAULT CURRENT_TIMESTAMP NULL,
    imported boolean DEFAULT FALSE,
    partner_id int4 NULL,
    aw_deep_link text NULL,
    product_name text NULL,
    aw_product_id text NULL,
    merchant_product_id text NULL,
    merchant_image_url text NULL,
    description text NULL,
    merchant_category text NULL,
    search_price text NULL,
    merchant_name text NULL,
    merchant_id text NULL,
    category_name text NULL,
    category_id text NULL,
    aw_image_url text NULL,
    currency text NULL,
    store_price text NULL,
    delivery_cost text NULL,
    merchant_deep_link text NULL,
    "language" text NULL,
    last_updated text NULL,
    display_price text NULL,
    data_feed_id text NULL,
    brand_name text NULL,
    brand_id text NULL,
    colour text NULL,
    product_short_description text NULL,
    specifications text NULL,
    "condition" text NULL,
    product_model text NULL,
    model_number text NULL,
    dimensions text NULL,
    keywords text NULL,
    promotional_text text NULL,
    product_type text NULL,
    commission_group text NULL,
    merchant_product_category_path text NULL,
    merchant_product_second_category text NULL,
    merchant_product_third_category text NULL,
    rrp_price text NULL,
    saving text NULL,
    savings_percent text NULL,
    base_price text NULL,
    base_price_amount text NULL,
    base_price_text text NULL,
    product_price_old text NULL,
    delivery_restrictions text NULL,
    delivery_weight text NULL,
    warranty text NULL,
    terms_of_contract text NULL,
    delivery_time text NULL,
    in_stock text NULL,
    stock_quantity text NULL,
    valid_from text NULL,
    valid_to text NULL,
    is_for_sale text NULL,
    web_offer text NULL,
    pre_order text NULL,
    stock_status text NULL,
    size_stock_status text NULL,
    size_stock_amount text NULL,
    merchant_thumb_url text NULL,
    large_image text NULL,
    alternate_image text NULL,
    aw_thumb_url text NULL,
    alternate_image_two text NULL,
    alternate_image_three text NULL,
    alternate_image_four text NULL,
    reviews text NULL,
    average_rating text NULL,
    rating text NULL,
    number_available text NULL,
    custom_1 text NULL,
    custom_2 text NULL,
    custom_3 text NULL,
    custom_4 text NULL,
    custom_5 text NULL,
    custom_6 text NULL,
    custom_7 text NULL,
    custom_8 text NULL,
    custom_9 text NULL,
    ean text NULL,
    isbn text NULL,
    upc text NULL,
    mpn text NULL,
    parent_product_id text NULL,
    product_gtin text NULL,
    basket_link text NULL,
    fashion_suitable_for text NULL,
    fashion_category text NULL,
    fashion_size text NULL,
    fashion_material text NULL,
    fashion_pattern text NULL,
    fashion_swatch text NULL,
    CONSTRAINT awin_catalogo_import_temp_pkey PRIMARY KEY (id)
);
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

def recreate_awin_catalogo_import_temp(conn):
    with conn.cursor() as cur:
        cur.execute(TABLE_DDL)
    conn.commit()
    log("Table awin_catalogo_import_temp dropped and recreated.", icon="🗑️")

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
            sql=f"COPY awin_catalogo_import_temp ({columns}) FROM STDIN WITH CSV",
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
        recreate_awin_catalogo_import_temp(conn)
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

