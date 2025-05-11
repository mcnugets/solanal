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

    def __init__(self, logger: logger, base_file, columns: Optional[List[str]] = None):
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

    def process_data(self, data: List[str] | Dict) -> Dict:
        try:
            if self.columns is None:
                return data

            # Convert list to DataFrame row
            data_len = len(data)
            expected_len = len(self.columns)
            col = self.columns[::-1]
            data = data[::-1]
            row_dict = {}
            if data_len != expected_len:
                self.logger.log_warning(
                    f'mismatch between the data and the columns length, expected {expected_len}, got {data_len}'
                )
               
                if data_len < expected_len:
                    
                    if data_len == expected_len - 1:
                        
                        check_latest_el = data[-1]
                        second_last_el = data[-2]
                        third_last = data[-3]
                       
                       
                       
                        if check_latest_el in second_last_el and third_last not in ["Buy","Run"]:
                            data.pop()

                        
                        data = data[::-1]
                        
                        for col in col:
                            print(data[-1])
                            if col == "Top 10":
                                if data[-1][-1] == '%':
                                    row_dict[col] = data.pop()
                                    continue
                                row_dict[col] = ""
                                continue
                                        
                            
                            if col == "Dev holds": 
                                if data[-1][-1] == '%':
                                    row_dict[col] = data.pop()
                                    continue
                                row_dict[col] = ""
                                continue
                            row_dict[col] = data.pop()
                                

                    if data_len ==  expected_len - 2:
                        data = data[::-1]
                
                        for col in col:
                            if col == "Top 10":
                                row_dict[col] = ""
                                continue
                            if col == "Dev holds":
                                row_dict[col] = ""
                                continue
                            row_dict[col] = data.pop()
                        self.logger.log_info(f' balls itch {row_dict}')
                   

            if not row_dict:
                row_dict = dict(zip(col, data))
                self.logger.log_info(f' the row dict BALLS{row_dict}')
            # row_dict = {
            #     col: val for col, val in zip_longest(self.columns, data, fillvalue="")
            # }
            # if "" in row_dict:
            #     row_dict.pop("")

            self.logger.log_info(f"the data in dataframe manager: {row_dict}")

            # section for adding to queue

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
        "dev sold/bought",
        "age",
        "address",
        "liquidity",
        "total holders",
        "Top 10",
        "Dev holds",
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
data_sample_3 = ['0x', '0xa', '0xa', 'Buy', '1s', 'Gq7XD...oop', '$0', '--', '$0', '$0', 'Gq7XDXZ3ZYxfXHbpbtRsL5S7EmiwpW68vn1BKrQboop']


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