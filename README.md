# llm solana analaizah

> [!WARNING]  
> 🚧 KEEP IN MIND THAT THE PROJECT IS UNDER DEVELOPMENT 🚧
## Project Description
This tool is designed to analyze degen coins on the Solana blockchain by scraping relevant data and using Large Language Models (LLMs) for pattern identification and inference.

## Setup

### Prerequisites
- Python 3.x installed.
- Git installed.
- A virtual environment tool (like `venv` or `conda`).

### Cloning the Repository
First, clone the project repository to your local machine:

```bash
git clone <repository_url> # Replace with your actual repository URL
cd "degen coin analysis tool"
```

### Setting up the Virtual Environment
It's highly recommended to use a virtual environment to manage project dependencies and avoid conflicts with other Python projects.
```bash
# Navigate to the project root if not already there
cd degen coin analysis tool

# Using venv (common with Python 3.3+)
python -m venv .venv

# Activate the virtual environment
# On macOS/Linux:
source .venv/bin/activate

# On Windows:
# .venv\Scripts\activate
```

### Installing Dependencies
Once your virtual environment is active, install the required packages listed in `requirements.txt`:

```bash
pip install -r requirements.txt
```

### Ollama Setup

Currently project solely relies on locally setup LLM(Ollama), so for it to run you need the following:

1.  **Download and Install Ollama:**
    *   **On macOS and Windows:** Visit the [Ollama website](https://ollama.com/download) and download the appropriate installer for your operating system. Follow the installation instructions.
    *   **On Linux:** Open your terminal and run the following command:
        ```bash
        curl -fsSL https://ollama.com/install.sh | sh
        ```
        This script will install Ollama to `~/.local/bin` and set it up as a systemd service.
2.  **Verify Installation:** Open your terminal and run `ollama --version` to ensure it's installed correctly. You should see the installed version.
3.  **Pull the LLM Model:**
    - You'll need to download the LLM model using Ollama CLI
    - Replace `<model_name>` with the model specified in your `config.json`
    
    ```bash
    ollama pull <model_name>  # Example: ollama pull deepseek-r1:7b
    ```
    
    *Note: The model name must match exactly what's in your configuration file.*

Ensure the Ollama application is running (usually starts automatically after installation on Linux/macOS or as a background process on Windows) when you use the tool for LLM analysis.

## Configuration (`config.json`)

This project uses a `config.json` file located in the project root directory to manage various settings, API keys, and parameters required for scraping and LLM analysis. Keeping configurations in this file allows you to easily change settings without modifying the code and helps in managing sensitive information.

**You must create or update the `config.json` file** with your specific details. Look for a `config.json.example` or similar file in the repository if one exists; otherwise, create `config.json` from scratch based on the required parameters and the structure below.

A typical `config.json` for this project might include (but is not limited to):

-   `"llm_api_key"`: Your API key for the Large Language Model provider.
-   `"scraping_urls"`: A list of URLs or endpoints to scrape data from.
-   `"data_output_path"`: Directory path where scraped or analyzed data should be saved.
-   `"llm_model_name"`: The specific model name to use for LLM analysis.
-   `"analysis_threshold"`: A numerical parameter used in the analysis logic.

**Example `config.json` structure (Illustrative - Adapt to your project's needs):**

```json
{
    "global": {
        "data_sources": ["YOUR_DATA_SOURCE_1", "YOUR_DATA_SOURCE_2"],
        "cleaning_patterns": {
            "\\n+": "#",
            "\\#+": "#",
            "^\\#|\\#$": ""
        }
    },
    "scrapers": {
        "pumpfun": {
            "scraper": true,
            "wait": false,
            "save": true,
            "process": true,
            "scraper_configs": {
                "type": "pumpfun",
                "url": "YOUR_PUMPFUN_URL",
                "row_locator": "YOUR_LOCATOR",
                "popup_locator": "YOUR_LOCATOR",
                "main_locator": "YOUR_LOCATOR",
                "div_locator": "YOUR_LOCATOR"
            },
            "columns": [
                "YOUR_COLUMN_1",
                "YOUR_COLUMN_2"
            ],
            "patterns": [
                "YOUR_PATTERN_1",
                "YOUR_PATTERN_2"
            ],
            "base_file": "YOUR_BASE_FILE.csv",
            "input_queue": null
        },
        "gmgn_2": {
             "scraper": true,
            "wait": false,
            "save": true,
            "process": true,
            "scraper_configs": {
                "type": "gmgn_2",
                "url": "YOUR_GMGN_2_URL",
                "row_locator": "YOUR_LOCATOR",
                "popup_locator": "YOUR_LOCATOR",
                "main_locator": "YOUR_LOCATOR",
                "extra_locator": "YOUR_LOCATOR"
            },
             "columns": [
                "YOUR_COLUMN_1",
                "YOUR_COLUMN_2"
            ],
            "patterns": [
                "YOUR_PATTERN_1",
                "YOUR_PATTERN_2"
            ],
            "base_file": "YOUR_BASE_FILE.csv",
            "input_queue": null,
            "output_queue": "YOUR_QUEUE_NAME"
        },
        "gmgn": {
             "scraper": true,
            "wait": true,
            "save": true,
            "process": true,
            "scraper_configs": {
                "type": "gmgn",
                "url": "YOUR_GMGN_URL",
                "row_locator": "YOUR_LOCATOR",
                "popup_locator": "YOUR_LOCATOR",
                "main_locator": "YOUR_LOCATOR",
                "csv_path": "YOUR_CSV_PATH.csv"
            },
             "columns": [
                "YOUR_COLUMN_1",
                "YOUR_COLUMN_2"
            ],
            "patterns": [
                "YOUR_PATTERN_1",
                "YOUR_PATTERN_2"
            ],
            "base_file": "YOUR_BASE_FILE.csv",
             "input_queue": "YOUR_QUEUE_NAME",
            "output_queue": "YOUR_QUEUE_NAME"
        },
        "solscan": {
             "scraper": true,
            "wait": true,
            "save": true,
            "process": false,
            "scraper_configs": {
                "type": "solscan",
                "url": "YOUR_SOLSCAN_URL",
                "row_locator": "YOUR_LOCATOR",
                "popup_locator": "YOUR_LOCATOR",
                "main_locator": "YOUR_LOCATOR",
                "csv_path": "YOUR_CSV_PATH.csv",
                "download_path": "YOUR_DOWNLOAD_PATH"
            },
             "columns": [],
            "patterns": {},
            "base_file": "",
             "input_queue": "YOUR_QUEUE_NAME",
            "output_queue": "YOUR_QUEUE_NAME"
        }
    },
    "llm": {
        "batch": 1,
        "model": "YOUR_LLM_MODEL_NAME",
        "input_queue": "YOUR_QUEUE_NAME",
        "output_queue": "YOUR_QUEUE_NAME"
    }
}
```

**Remember to replace placeholder values (like URLs, API keys, locators, queue names, etc.) with your actual configuration based on `src/core/config.py`.**



## How to Run

```bash
# Make sure your virtual environment is active
source .venv/bin/activate # or .venv\Scripts\activate

python main.py
```

