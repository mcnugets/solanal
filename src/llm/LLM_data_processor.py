"""
# LLM Data Processor for Solana Token Analysis
================================================

## Overview
This module processes and prepares data for LLM analysis of Solana tokens. It handles:
- Token basic data
- Extended token metrics
- Holder information and patterns

## Key Features
- Batch processing of token data
- Asynchronous data loading
- Holder information retrieval
- CSV file management
- Memory-efficient data handling

## Data Flow
1. Loads token data from CSV files
2. Processes holder information
3. Combines multiple data sources
4. Yields structured data for LLM analysis

## Usage Example
```python
files = {
    "token_data": "path/to/pumpfun_data.csv",
    "more_token_data": "path/to/gmgn_data.csv",
    "holders": "path/to/holders_directory"
}
processor = llm_data_processor(files, batch_size=10)
for data in processor.load_data():
    process_token_data(data)
```

## Dependencies
- pandas: Data manipulation and CSV handling
- pathlib: File path operations
- typing: Type annotations
"""

import pandas as pd

from pathlib import Path
from typing import Dict, Any, Generator, Optional, List, Annotated
import time
from dataclasses import dataclass
from collections import deque

# from token_valid import token_data_validator
# from src import ScraperLogger as logger
# from src import valid_data, gmgn_main_data, gmgn_data, holders_data

from ..core.logger import ScraperLogger as logger
from ..data.llm_model import valid_data, gmgn_main_data, gmgn_data, holders_data
from .token_valid import token_data_validator


class llm_data_processor:

    def __init__(
        self,
        logger: logger,
        batch_size: int,
    ) -> None:

        self.batch_size = batch_size
        self.deque = deque(maxlen=batch_size)
        self.logger = logger
        self.data_validator = token_data_validator(logger)

    def process_data(
        self,
        data: Annotated[
            Dict[str, Any],
            "This dict needs to have keys: pumpfun, gmgn, holders",
        ],
    ):

        try:
            validated_data = self.data_validator.validate(data)
            if not validated_data:
                return None

            return self.setup_prompt(validated_data)
        except Exception as e:
            self.logger.log_error(error_msg=f"Error processing data:", exc_info=e)
            return None

    def setup_prompt(self, validated_data: valid_data) -> str:
        try:
            columns = ["**Field**", "**Value**"]
            main_token_data = self.setup_token_data(
                validated_data.pumpfun_data, columns
            )
            gmgn_data = self.setup_gmgn_data(validated_data.gmgn_data, columns)
            holders = self.setup_holders(validated_data.holders)

            divider = "-" * 50
            return f"""
            {divider}
            
**Token Data:**
{main_token_data}

{divider}

**Additional token:**
{gmgn_data}

{divider}

**Holders Data:**
{holders}

{divider}"""

        except Exception as e:
            self.logger.error(f"Error setting up prompt: {e}")
            return None

    def setup_holders(self, holders: holders_data):
        holders_dict = holders.model_dump()
        print(holders_dict)
        holders_df = pd.DataFrame.from_dict(holders_dict)
        return holders_df.to_string()

    # ["**Field**", "**Value**"]
    def setup_token_data(self, token_data: gmgn_main_data, columns: List[str]):
        token_df = pd.DataFrame.from_dict(token_data)
        token_df.columns = columns
        return token_df.to_string(index=False)

    def setup_gmgn_data(self, gmgn_data: gmgn_data, columns: List[str]):
        gmgn_df = pd.DataFrame.from_dict(gmgn_data)
        gmgn_df.columns = columns

        return gmgn_df.to_string(index=False)


def get_holders(address: str, holders) -> Optional[Dict[str, Any]]:

    try:
        holders_dr = Path(holders)
        ca = f"{address}_data"

        files = list(holders_dr.rglob(f"{ca}.csv"))
        if not files:
            logger.error(f"No holder data files found for address: {address}")
            return None

        return pd.read_csv(files[0]).to_dict()
    except Exception as e:
        logger.error(f"Error loading holders data: {e}")
        return None

    # def find_holders_file(self, address: str, path: str) -> Optional[Path]:
    #     dir_path = Path(path)
    #     for file in dir_path.rglob(f"{address}_data.csv"):
    #         if file.is_file():
    #             return file
    #     return None


if __name__ == "__main__":

    pump_fun_data = get_holders(
        "4eD8PR3sxyMqT2wzCnqQfT3QCJao6EbijjB2zbik3mFN_data", "../../holders/"
    )
    print(pump_fun_data)
    # df = pd.DataFrame.from_dict(pump_fun_data["0xabc123"], orient="index").T
    # print(df.to_string())

    # d = {"pumpfun_data": {"one": 1}, "gmgn_data": {"two": 2}, "holders": {"three": 3}}
    # data = valid_data(**d)
    # print(data)
    #     # Define file paths relative to script location
    #     base_path = Path(__file__).resolve().parent.parent.parent
    #     files = {
    #         "token_data": str(base_path / "pumpfun_data.csv"),
    #         "more_token_data": str(base_path / "gmgn_data.csv"),
    #         "holders": str(base_path / "holders"),
    #     }

    #     # Initialize processor
    #     processor = llm_data_processor(files, batch_size=1)

    #     # Process and analyze data
    #     for data in processor.load_data():

    #         print("\nProcessing Token Data:")
    #         if "token_data" in data.keys():
    #             print(f"Address: {data['token_data'].get('full_address')}")

    #         if "more_token_data" in data.keys():
    #             print("\nAdditional Token Info:")
    #             print(pd.DataFrame([data["more_token_data"]]).T)

    #         if data["holders"]:
    #             print(f"\nHolders Info: {len(data['holders'])} holders found")
    #             print(data["holders"])
    #         else:
    #             print("\nNo holders data available")

    #         print("-" * 50)

    # except FileNotFoundError as e:
    #     print(f"Error: Required file not found - {e}")
    # except Exception as e:
    #     print(f"Error processing data: {e}")
