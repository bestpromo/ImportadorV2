# AWIN Catalog Importer

This project provides a Python script to import CSV product catalogs from AWIN into a PostgreSQL database, using batch inserts and robust logging.

## Features

- **Automatic Table Recreation:**  
  The script drops and recreates the `awin_catalogo_import_temp` table before each import, ensuring a clean state and resetting the primary key sequence.

- **Batch Import with COPY:**  
  Uses PostgreSQL's `COPY` command for fast, batch CSV import. Batch size is configurable via `.env` (`BATCH_SIZE`, default: 5000).

- **Partner ID Injection:**  
  The value of `AWIN_PARTNER_ID` from `.env` is automatically inserted into the `partner_id` column for every imported row.

- **Column Name Normalization:**  
  All CSV column names are converted to lowercase and `:` is replaced with `_` to match PostgreSQL conventions.

- **Logging with Icons:**  
  Each run generates a log file in `data/awin/` with a timestamped name. Logs include icons for easy reading and track process start, file processing, and completion times.

- **Environment Configuration:**  
  All credentials and settings are managed via a `.env` file.

## Usage

1. **Configure your `.env` file:**

    ```env
    # AWIN credentials
    AWIN_API_KEY=...
    AWIN_PUBLISHER_ID=...
    AWIN_PARTNER_ID=...

    # Batch size (optional)
    BATCH_SIZE=10000

    # PostgreSQL credentials
    DB_HOST=...
    DB_PORT=5432
    DB_USER=...
    DB_PASSWORD=...
    DB_DATABASE=...
    ```

2. **Place your CSV files in:**
    ```
    data/awin/
    ```

3. **Run the script:**
    ```bash
    python3 [awin_catalog_importcsvs.py](http://_vscodecontentref_/0)
    ```

4. **Check logs:**
    - Log files are created in `data/awin/` with the format `DDMMYYYY_HHMMSS.log`.
    - Logs include icons for process steps (start 🚀, file 📄, batch ✅, finish 🏁, etc).

## Table Structure

The script creates the following table on each run:

```sql
CREATE TABLE public.awin_catalogo_import_temp (
    id serial4 NOT NULL,
    created_at timestamp DEFAULT CURRENT_TIMESTAMP NULL,
    partner_id int4 NULL,
    aw_deep_link text NULL,
    product_name text NULL,
    ...
    fashion_swatch text NULL,
    CONSTRAINT awin_catalogo_import_temp_pkey PRIMARY KEY (id)
);
```