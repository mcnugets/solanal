import pandas as pd
from typing import List, Optional, Dict
from datetime import datetime
import logging
from pathlib import Path
from src.data.models import Address_Data as ad
import csv
from src.core.logger import ScraperLogger as logger
from itertools import zip_longest


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

    def __init__(self, logger: logger, scraper_type: str, base_file, columns: Optional[List[str]] = None):
        
        self.scraper_type = scraper_type
        self.df = pd.DataFrame()
        self.base_file = base_file
        self.columns = columns
        self.setup_logging()
        self.logger = logger

    def setup_logging(self):
        logging.basicConfig(
            filename=f"dataframe_{datetime.now():%Y%m%d_%H%M%S}.log",
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
        )
    # def gmgn_main(self, data: List[str]) -> Dict[str, str]:
    
    #     try:
    #         CORE_LABELS = 7
    #         map_core = {}
    #         gmgn_2_copy = self.columns.copy()  # Use self.columns instead of undefined gmgn_2
            
    #         # Handle percentage case in core data
    #         if '%' in data[CORE_LABELS]:
    #             index = len(self.columns) - (CORE_LABELS - 1)
    #             map_core[self.columns[index]] = None
    #             gmgn_2_copy.pop(index)
    #             CORE_LABELS -= 1
                
    #         # Map core labels
    #         for i in range(min(CORE_LABELS, len(data))):
    #             map_core[gmgn_2_copy[i]] = data[i]
           
    #         # Map last 3 items (volume, market cap, full_address)
    #         N_ITER = 3
    #         map_last = {}
    #         for i in range(min(N_ITER, len(data))):
    #             map_last[self.columns[-i - 1]] = data.pop()
                
    #         logging.info(f'Mapped last items: {map_last}')
    #         new_mapped_data = {**map_core, **map_last}
    #         logging.info(f'Final mapped data: {new_mapped_data}')
    #         return new_mapped_data
            
    #     except Exception as e:
    #         logging.error(f'Error processing GMGN data: {e}')
    #         return {}
    
    def gmgn_main(self, data: List[str]) -> Dict[str, str]:
    
        try:
            # Extract and validate address
            address_part = data[3].partition('.')[0]
            self.logger.log_info(f'Validating address: {address_part}')
            
            if address_part not in data[-1]:
                data = data[1:]  # Skip first element if address doesn't match
                
            # Prepare data for DataFrame
            row_data = data[:len(self.columns)-1] + [data[-1]]  # Combine all but last with last
            
            # Create dictionary mapping columns to values
            row_dict = dict(zip(self.columns, row_data))
            
            self.logger.log_info(f'Processed row data: {row_dict}')
            return row_dict
            
        except Exception as e:
            self.logger.log_error(f'Error processing GMGN data: {e}')
            return {}
    
    def gmgn_secondary(self, data: List[str]) -> Dict[str, str]:
        return  dict(zip(self.columns, data))
    def run_map_strategy(self, scraper_type: str, data: List[str]):
        row_dict = None
        if scraper_type == "gmgn_2":
            row_dict = self.gmgn_main(data)
        if scraper_type == "gmgn":
            row_dict = self.gmgn_secondary(data)
        return row_dict

    def process_data(self, data: List[str] | Dict) -> Dict:
        try:
            if self.columns is None:
                return data
  
            # section for adding to queue
            row_dict = self.run_map_strategy(self.scraper_type, data=data)

            new_row = pd.DataFrame([row_dict])
            new_row = new_row.astype(str)
            # Append to main DataFrame
            self.df = pd.concat([self.df, new_row], ignore_index=True)

            logging.info(f"row details {row_dict}")
            logging.info(f"Added row. Row details: {len(self.df)}")
            columnname = self.columns[-1]
            # Save checkpoint every 100 rows
            if len(self.df) % 1 == 0:
                self.clean_dataframe(columnname=columnname)
                self.save_checkpoint()
            return row_dict
        except Exception as e:
            self.logger.log_error(f"Error processing data: {e}")

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
            # backup_base_file = base_file + "_backup"
            # backup_csv = f"{backup_base_file}_{timestamp}.csv"
            # backup_excel = f"{backup_base_file}_{timestamp}.xlsx"
            # updated_df.to_csv(backup_csv, index=False)
            # updated_df.to_excel(backup_excel, index=False)

            # logging.info(f"Saved {len(updated_df)} rows to {base_file}")
            # logging.info(f"Backup created: {backup_csv}")

        except Exception as e:
            logging.error(f"Error saving checkpoint: {e}")

    def get_stats(self) -> dict:
        return {
            "total_rows": len(self.df),
            "missing_values": self.df.isna().sum().to_dict(),
            "duplicates": len(self.df[self.df.duplicated()]),
        }


gmgn = [
    "ticker",
    "name",
    "i dont know",
    "dev sold?",
    "address",
    "current price",
    "24h",
    "snipers",
    "bluechip",
    "top 10",
    "audit",
    "Taxes",
    "full_address",
]

gmgn_2 = [
        "ticker",
        "name",
        "age",
        "address",
        "migrated",
        "total holders",
        "TX",
        "volume",
        "market cap",
        "full_address",
    ]


data_sample = [
    "6p8ez...Aq4",
    "$0.0000",
    "--%",
    "3/4",
    "0%",
    "0.4%",
    "4/4",
    "1%",
    "6p8ez2tKSKhyCZpv29sxd5fwpzS6uDpW515hUybvSAq4",
]
data_sample_2 = [
    "11cfd...ebp",
    "$0.0000",
    "--%",
    "--",
    "0%",
    "Audit",
    "11cfd6acd78d06c7c555f91a427e9d10.webp",
]
data_sample_3 = ['NODEGO', 'NODEGOAI', '25s', 'BbaqD...mHC', '1', '2', '0%', '0%', 'Run', '$315.4', '$68.9K', 'wpeori345345pump']


def main():
    """Main function for testing DataFrameManager functionality."""
    import pandas as pd
    from DataFrameManager import DataFrameManager
    
    # Initialize DataFrameManager with test columns
    test_columns = ["ticker", "name", "address", "liquidity", "market_cap"]
    df_manager = DataFrameManager(columns=gmgn_2, base_file="pumpfun_data.csv", logger=logger())
    
    ans = df_manager.process_data(data_sample_3)
    print(ans)
 
   
    
if __name__ == "__main__":
    main()