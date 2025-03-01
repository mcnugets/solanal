import pandas as pd
from pathlib import Path
from typing import Dict, Any, Generator, Optional
import time


class llm_data_processor:
    def __init__(self, files: Dict[str, str], batch_size: int) -> None:
        self.files = files
        self.more_token_data = pd.read_csv(files["more_token_data"]).T
        self.token_data = pd.read_csv(files["token_data"])
        self.holders = list(Path(self.files["holders"]).rglob("*.csv"))
        self.batch_size = batch_size

    def load_data(self) -> Generator[Dict[str, Any], None, None]:

        more_token_data = self.more_token_data
        token_data = self.token_data

        new_data = {}
        for i in more_token_data:
            ca = more_token_data[i]["full_address"]
            holders_info = self.get_holders(address=ca)

            # address_list = token_data["full_address"].to_list()

            # if more_token_data[i]["full_address"] in address_list:

            row = token_data.loc[
                token_data["full_address"] == more_token_data[i]["full_address"]
            ]
            if not row.empty:
                new_data["token_data"] = row.to_dict()

            new_data["holders"] = holders_info
            new_data["more_token_data"] = more_token_data[i].to_dict()

            time.sleep(2)
            yield new_data

    def get_holders(self, address: str) -> Optional[Dict[str, Any]]:

        try:
            ca = f"{address}_data"

            found_file = next((file for file in self.holders if file.stem == ca), None)

            if found_file:
                return pd.read_csv(found_file, dtype=str).to_dict()
        except Exception as e:
            print(f"Error reading holders file for address {address}: {e}")
        return None

    def find_holders_file(self, address: str, path: str) -> Optional[Path]:
        dir_path = Path(path)
        for file in dir_path.rglob(f"{address}_data.csv"):
            if file.is_file():
                return file
        return None


if __name__ == "__main__":
    try:
        # Define file paths relative to script location
        base_path = Path(__file__).resolve().parent.parent.parent
        files = {
            "token_data": str(base_path / "pumpfun_data.csv"),
            "more_token_data": str(base_path / "gmgn_data.csv"),
            "holders": str(base_path / "holders"),
        }

        # Initialize processor
        processor = llm_data_processor(files, batch_size=1)

        # Process and analyze data
        for data in processor.load_data():

            print("\nProcessing Token Data:")
            if "token_data" in data.keys():
                print(f"Address: {data['token_data'].get('full_address')}")

            if "more_token_data" in data.keys():
                print("\nAdditional Token Info:")
                print(pd.DataFrame([data["more_token_data"]]).T)

            if data["holders"]:
                print(f"\nHolders Info: {len(data['holders'])} holders found")
                print(data["holders"])
            else:
                print("\nNo holders data available")

            print("-" * 50)

    except FileNotFoundError as e:
        print(f"Error: Required file not found - {e}")
    except Exception as e:
        print(f"Error processing data: {e}")
