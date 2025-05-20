# ImportadorV2 - AWIN Catalog Integration

This project automates the ingestion of product catalogs provided by AWIN, downloading compressed CSV files, filtering active stores, and saving the catalogs ready for use in e-commerce systems.

## Features

- Downloads the AWIN catalog list (.gz file), extracts, and saves as CSV.
- Filters only stores with **active** status.
- Downloads and extracts catalogs from active stores.
- Saves detailed process logs.

## Folder Structure

```
ImportadorV2/
│
├── data/             # directory for downloaded files (DO NOT version)  
│   └── awin/
│       ├── lists/    # Main list and execution logs
│       └── inputs/   # Catalogs from active stores
│
├── src/
│   └── awin_catalog_downloader.py
│
├── .env              # access variables (DO NOT version)
├── .gitignore
├── requirements.txt
└── README.md
```

## Setup

1. **Clone the repository**
2. **Create the `.env` file in the project root:**
    ```
    AWIN_API_KEY=your_apikey
    AWIN_PUBLISHER_ID=your_publisher_id
    ```
3. **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Execution

Run the main script:

```bash
python src/awin_catalog_downloader.py
```

Monitor the progress in the terminal and in the log file generated in `data/awin/lists/`.

## Notes

- The `.env` file **MUST NOT** be versioned.
- Downloaded files can be large, make sure you have enough disk space.
- The script can be adapted to run via cron or orchestrators.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

**Author:** André Luiz Faustino