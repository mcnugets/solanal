from typing import Dict, Any, Optional
from src import ScraperLogger as logger
from pathlib import Path
import pandas as pd
from src import llm_data_processor
from src import holders_data, valid_data, gmgn_main_data, gmgn_data
from src import llm_analyser
from collections import deque

log = logger()


def get_holders(address: str, holders) -> Optional[Dict[str, Any]]:

    try:
        holders_dr = Path(holders)
        ca = f"{address}_data.csv"

        script_dir = Path(__file__).parent
        holders_dir = script_dir.parent / "holders"
        files = list(holders_dir.glob("*.csv"))
        if not files:
            log.log_error(
                error_msg=f"No holder data files found for address: {address}"
            )
            return None
        for f in files:
            s_files = f.name.split("\\")
            if s_files[0] == ca:
                return pd.read_csv(f).to_dict()

    except Exception as e:
        log.log_error(error_msg=f"Error loading holders data:", exc_info=e)
        return None


def load_data(gmgn, address):

    parent_dir = Path(__file__).parent
    csv_file = parent_dir.parent / gmgn
    gmgn_data = pd.read_csv(csv_file).to_dict()
    df = pd.DataFrame.from_dict(gmgn_data).T.to_dict()
    new_data = {}
    for i in df.keys():

        # address_list = token_data["full_address"].to_list()

        # if more_token_data[i]["full_address"] in address_list:

        if address == df[i]["full_address"]:
            return df[i]


if __name__ == "__main__":

    hodler_data = get_holders(
        "4eD8PR3sxyMqT2wzCnqQfT3QCJao6EbijjB2zbik3mFN", "../holders/"
    )
    loaded_data = load_data(
        "gmgn_data.csv", "3HsSU5nZ4du6Zd4VNDMDsmkDeX1VLkiQc9RiPQU7pump"
    )
    loadded_data2 = load_data(
        "pumpfun_data.csv", "3HsSU5nZ4du6Zd4VNDMDsmkDeX1VLkiQc9RiPQU7pump"
    )

    llm_p = llm_data_processor(log, batch_size=15)

    # df = pd.DataFrame.from_dict(pump_fun_data["0xabc123"], orient="index").T
    data = {
        "pumpfun": loadded_data2,
        "gmgn": loaded_data,
        "holders": hodler_data,
    }
    d = deque()
    d.append(data)
    analysis = llm_analyser(
        model="deepseek-r1:7b", logger=log, llm_data_processor=llm_p, deque=d
    )
    print(analysis.analyse())
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
