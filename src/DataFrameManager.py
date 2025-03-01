import pandas as pd
from typing import List, Optional
from datetime import datetime
import logging
from pathlib import Path

import csv


# [
#     "name",
#     "bd",
#     "mc",
#     "vol",
#     "t10",
#     "holders",
#     "age",
#     "dh",
#     "snipers",
#     "address",
# ]
class DataFrameManager:
    def __init__(self, base_file, columns: Optional[List[str]] = None):
        self.df = pd.DataFrame()
        self.base_file = base_file
        self.columns = columns
        self.setup_logging()

    def setup_logging(self):
        logging.basicConfig(
            filename=f"dataframe_{datetime.now():%Y%m%d_%H%M%S}.log",
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
        )

    def process_data(self, data: List[str], columnname: str) -> None:
        try:
            # Convert list to DataFrame row
            row_dict = dict(zip(self.columns, data))
            print("---------------------")
            print(f"row_dict: {row_dict}")
            print("---------------------")

            # section for adding to queue

            new_row = pd.DataFrame([row_dict])
            new_row = new_row.astype(str)
            # Append to main DataFrame
            self.df = pd.concat([self.df, new_row], ignore_index=True)

            logging.info(f"row details {row_dict}")
            logging.info(f"Added row. Row details: {len(self.df)}")

            # Save checkpoint every 100 rows
            if len(self.df) % 25 == 0:
                self.clean_dataframe(columnname=columnname)
                self.save_checkpoint()

        except Exception as e:
            logging.error(f"Error processing data: {e}")

    def clean_dataframe(self, columnname: str) -> None:
        try:
            self.df = self.df.replace("", pd.NA)  # Replace empty strings
            self.df = self.df.dropna(how="all")  # Drop empty rows
            self.df = self.df.drop_duplicates(subset=columnname)  # Remove duplicates
        except Exception as e:
            logging.error(f"Error cleaning DataFrame: {e}")

    def save_checkpoint(self) -> None:
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_file = self.base_file

            if Path(base_file).exists():
                # Load existing and append
                existing_df = pd.read_csv(base_file)
                updated_df = pd.concat([existing_df, self.df], ignore_index=True)
                # Remove duplicates
                updated_df = updated_df.drop_duplicates(subset=self.columns[0])
            else:
                updated_df = self.df

            # Save updated DataFrame
            updated_df.to_csv(base_file, index=False, quoting=csv.QUOTE_ALL)

            # Save backup with timestamp
            backup_base_file = base_file + "_backup"
            backup_csv = f"{backup_base_file}_{timestamp}.csv"
            backup_excel = f"{backup_base_file}_{timestamp}.xlsx"
            updated_df.to_csv(backup_csv, index=False)
            updated_df.to_excel(backup_excel, index=False)

            logging.info(f"Saved {len(updated_df)} rows to {base_file}")
            logging.info(f"Backup created: {backup_csv}")

        except Exception as e:
            logging.error(f"Error saving checkpoint: {e}")

    def get_stats(self) -> dict:
        return {
            "total_rows": len(self.df),
            "missing_values": self.df.isna().sum().to_dict(),
            "duplicates": len(self.df[self.df.duplicated()]),
        }


# Usage in CoinScraper
def _process_data(self):
    df_manager = DataFrameManager()
    while not self.stop_event.is_set():
        if not self.processed_queue.empty():
            data = self.processed_queue.get()
            df_manager.process_data(data)
