# ImportadorV2 - AWIN Catalog Integration

Automates the download, filtering, and preparation of AWIN product catalogs for use in e-commerce systems.

## Features

- Downloads the AWIN catalog list (.gz), extracts, and saves as CSV.
- Filters only stores with **active** status.
- Downloads and extracts catalogs from active stores.
- Generates detailed process logs.

## Folder Structure

```
ImportadorV2/
│
├── data/             # Downloaded files (DO NOT version)
│   └── awin/         # Catalogs from active stores   
│       └── lists/    # Main lists and execution logs
│
├── src/
│   └── awin_catalog_downloader.py
│
├── .env              # Access variables (DO NOT version)
├── .gitignore
├── requirements.txt
└── README.md
```

## General Rules

- **NEVER version files in `data/` or `.env`.**
- Always check for available disk space before running the script.
- Execution logs are stored in `data/awin/lists/`.
- The script can be scheduled via cron or orchestrators.
- For new integrations or adjustments, document in the README and keep the code clean and commented.

## Setup

1. **Clone the repository**
2. **Create the `.env` file at the root:**
    ```
    AWIN_API_KEY=your_apikey
    AWIN_PUBLISHER_ID=your_publisher_id
    ```
3. **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Execution

Run the main script:

```bash
python src/awin_catalog_downloader.py
```

Follow the progress in the terminal and in the generated log.

## Contribution

- Follow the code standard and keep dependencies updated.
- Describe relevant changes in this README.
- Open clear and objective PRs.

---

## License

MIT License. See the [LICENSE](LICENSE) file for more details.

**Author:** André Luiz Faustino